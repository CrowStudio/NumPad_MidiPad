#  * Copyright 2022 Daniel Arvidsson <daniel.arvidsson@crowstudio.se>
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with this
# program. If not, see <https://www.gnu.org/licenses/>.
#
# Credits to John Park, Adafruit Industries 2022 - for Macropad MIDI Tester
# and JEP_NeoTrellis_Blackbox_Triggers - who got me started to developing this piece of code.

from adafruit_macropad import MacroPad
from rainbowio import colorwheel
import time

WHITE = (255, 255, 255)
YELLOW = (230, 100, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
MINT = (0, 255, 50)

BKGND_COLOR = MAGENTA
PRESSED_COLOR = CYAN

SCREEN_ACTIVE = 60

CC_NUM0 = 7  # Volume
CC_NUM1 = 10 # Pan
CC_NUM2 = 1  # Modulation Wheel

# create the macropad object, rotate orientation, set state for startup config
macropad = MacroPad(rotation=0)
macropad.display.auto_refresh = False  # avoid lag
config_mode = 1

# --- Pixel setup --- #
macropad.pixels.brightness = 0.05
macropad.pixels[0] = YELLOW
macropad.pixels[2] = MAGENTA

# --- Display text setup --- #
blank_display = macropad.display_text("")
text_lines = macropad.display_text("Choose MacroPad mode:")
text_lines[0].text = "Yellow = NumPad"
text_lines[1].text = "Magenta = BlackBox"
text_lines.show()

encoder_map = ["+", "-", "*", "/", "(", ")", "%", "<-", ".", "="]

row = [3, 4]

key_map = []

key_maps = [['7', '8', '9',
             '4', '5', '6',
             '1', '2', '3',
             ',', '0', 'Enter'],
            [48, 49, 50,
             44, 45, 46,
             40, 41, 42,
             36, 37, 38],
            [48, 49, 51,
             44, 45, 47,
             40, 41, 43,
             36, 37, 39]]

keycode = [macropad.Keycode.KEYPAD_SEVEN,
           macropad.Keycode.KEYPAD_EIGHT,
           macropad.Keycode.KEYPAD_NINE,
           macropad.Keycode.KEYPAD_FOUR,
           macropad.Keycode.KEYPAD_FIVE,
           macropad.Keycode.KEYPAD_SIX,
           macropad.Keycode.KEYPAD_ONE,
           macropad.Keycode.KEYPAD_TWO,
           macropad.Keycode.KEYPAD_THREE,
           macropad.Keycode.COMMA,
           macropad.Keycode.KEYPAD_ZERO,
           macropad.Keycode.KEYPAD_ENTER]

encoder_keycode = [macropad.Keycode.KEYPAD_PLUS,
                   macropad.Keycode.KEYPAD_MINUS,
                   macropad.Keycode.KEYPAD_ASTERISK,
                   macropad.Keycode.KEYPAD_FORWARD_SLASH,
                   macropad.Keycode.EIGHT,
                   macropad.Keycode.NINE,
                   macropad.Keycode.FIVE,
                   macropad.Keycode.BACKSPACE,
                   macropad.Keycode.PERIOD,
                   macropad.Keycode.KEYPAD_EQUALS]

button_mode = 2  # button_mode 0 for NumPad / button_mode 1 for BlackBox / 2 is init mode

def configure_keypad(key_event):
    global config_mode
    global BKGND_COLOR
    global PRESSED_COLOR

    if key_event.pressed:
        if key_event.key_number == 0:
            set_button_mode(0)
            config_mode = 0
            BKGND_COLOR = YELLOW
            PRESSED_COLOR = WHITE
            macropad.pixels.brightness = 0.05
            set_pixel_color_mode()
        elif key_event.key_number == 2:
            set_button_mode(1)
            config_mode = 0
            BKGND_COLOR = MAGENTA
            PRESSED_COLOR = CYAN
            macropad.pixels.brightness = 0.05
            set_pixel_color_mode()


def set_button_mode(button_layout):
    global button_mode
    global key_map

    if button_layout == 0:
        button_mode = 0
        key_map = key_maps[0]
    elif button_layout == 1:
        button_mode = 1
        key_map = key_maps[1]


def set_pixel_color_mode():
    for key in range(12):
        set_background_colors(key)


def set_background_colors(key):
    if key == 9 and button_mode == 0:
        macropad.pixels[key] = CYAN
    elif key == 11 and button_mode == 0:
        macropad.pixels[key] = MAGENTA
    elif key in [2, 5, 8, 11] and row_4 == True:
        macropad.pixels[key] = MINT
    else:
        macropad.pixels[key] = BKGND_COLOR


def set_button_mode_text():
    if button_mode == 0:
        text_lines = macropad.display_text("NumPad")
        text_lines[0].text = f"Encoder character: {encoder_map[encoder_pos]}"
    elif button_mode == 1:
        text_lines = macropad.display_text("BlackBox MIDI")
        text_lines[0].text = f"{mode_text[encoder_mode]} {row[row_pos]}"
    return text_lines


def reset_pixel_to_bkgnd_color(key):
    set_background_colors(key)


def send_keypad_click(key):
    return macropad.keyboard.send(keycode[key])


def send_encoder_click(encoder_pos):
    if encoder_pos in [4, 5, 6]:
        return macropad.keyboard.press(macropad.Keycode.SHIFT, encoder_keycode[encoder_pos]), macropad.keyboard.release_all()
    else:
        return macropad.keyboard.send(encoder_keycode[encoder_pos])


def read_knob_value(knob):
    global knob_pos
    global encoder_pos
    global row_pos
    global knob_delta
    global last_knob_pos

    if button_mode == 0:
        encoder_pos = macropad.encoder % 10
    elif button_mode == 1 and knob in [0, 1, 2]:
        knob_pos = macropad.encoder
        knob_delta = knob_pos - last_knob_pos
        last_knob_pos = knob_pos
        cc_values[encoder_mode] = min(max(cc_values[encoder_mode] + knob_delta, 0), 31)  # scale the value
    else:
        row_pos = macropad.encoder % 2 


def send_cc_value(num):
    CC = [CC_NUM0, CC_NUM1, CC_NUM2]
    macropad.midi.send(macropad.ControlChange(CC[num], int(cc_values[encoder_mode]*4.1)))


def toggle_row():
    global key_map
    global row_4

    if row[row_pos] == 3:
        row_4 = False
        key_map = key_maps[1]
    else:
        row_4 = True
        key_map = key_maps[2]
    set_pixel_color_mode()


last_knob_pos = macropad.encoder  # store knob position state
knob_pos = 0
knob_delta = 0
encoder_mode = 3
encoder_pos = 0
row_pos = 0
mode_text = [f"CC # {CC_NUM0}:", f"CC #{CC_NUM1}:",
             f"CC # {CC_NUM2}:", "Active row:"]
cc_values = [0, 0, 0]  # initial CC values

row_4 = False

characters_entered = ""

loop_last_action = time.monotonic()
macropad_sleep = False

while True:
    loop_start_time = time.monotonic()
    if macropad.keys.events:  # check for key press or release
        text_lines.show()
        key_event = macropad.keys.events.get()
        if config_mode == 1:
            configure_keypad(key_event)
            text_lines = set_button_mode_text()

        elif key_event:
            if button_mode == 0:
                if key_event.pressed and macropad_sleep:
                    macropad_sleep = False
                    loop_last_action = time.monotonic()
                elif key_event.pressed:
                    key = key_event.key_number
                    macropad.pixels[key] = PRESSED_COLOR
                    if key_map[key] != "Enter":
                        send_keypad_click(key)
                        characters_entered = f"{characters_entered}{key_map[key]}"
                        text_lines[1].text = f"{characters_entered}"
                    else:
                        send_keypad_click(key)
                        characters_entered = ""
                elif key_event.released:
                    key = key_event.key_number
                    reset_pixel_to_bkgnd_color(key)

            if button_mode == 1:
                if key_event.pressed and macropad_sleep:
                    macropad_sleep = False
                    loop_last_action = time.monotonic()
                elif key_event.pressed:
                    key = key_event.key_number
                    macropad.midi.send(macropad.NoteOn(key_map[key], 120))
                    macropad.pixels[key] = PRESSED_COLOR
                    text_lines[2].text = f"SampleOn:{key_map[key]}"
                elif key_event.released:
                    key = key_event.key_number
                    macropad.midi.send(macropad.NoteOff(key_map[key], 0))
                    reset_pixel_to_bkgnd_color(key)
                    text_lines[2].text = ""

    macropad.encoder_switch_debounced.update()  # check the knob switch for press or release

    if macropad.encoder_switch_debounced.pressed:
        loop_last_action = time.monotonic()
        macropad.red_led = macropad.encoder_switch

    if macropad.encoder_switch_debounced.released:
        if button_mode == 0:
            send_encoder_click(encoder_pos)
            if encoder_map[encoder_pos] == "<-":
            	characters_entered = characters_entered[:-1]
            else:
                characters_entered = f"{characters_entered}{encoder_map[encoder_pos]}"
            text_lines[1].text = f"{characters_entered}"

        if button_mode == 1:
            encoder_mode = (encoder_mode+1) % 4
            if encoder_mode in [0, 1, 2]:
                text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"
            else:
                text_lines[0].text = f"{mode_text[encoder_mode]} {row[row_pos]}"
        macropad.red_led = macropad.encoder_switch

    if last_knob_pos is not macropad.encoder:  # knob has been turned
        loop_last_action = time.monotonic()
        if button_mode == 0:
            read_knob_value(0)
            text_lines[0].text = f"Encoder character: {encoder_map[encoder_pos]}"

        elif button_mode == 1:
            if encoder_mode in [0, 1, 2]:
                read_knob_value(encoder_mode)
                send_cc_value(encoder_mode)
                text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"

            else:
                read_knob_value(3)
                toggle_row()
                text_lines[0].text = f"{mode_text[encoder_mode]} {row[row_pos]}"
        last_knob_pos = macropad.encoder

    if (loop_start_time - loop_last_action) > SCREEN_ACTIVE:
        macropad.pixels.brightness = 0
        macropad_sleep = True
        blank_display.show()
    elif (loop_start_time - loop_last_action) < SCREEN_ACTIVE:
        macropad.pixels.brightness = 0.05
        macropad_sleep = False
        text_lines.show()

    macropad.display.refresh()