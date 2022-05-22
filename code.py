# SPDX-FileCopyrightText: 2022 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT
# Macropad MIDI Tester

from adafruit_macropad import MacroPad
from rainbowio import colorwheel

# --- Pixel Colors --- #
WHITE = (255, 255, 255)
YELLOW = (230, 100, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
MINT = (0, 255, 50)

BKG_COLOR = MAGENTA
PRESSED_COLOR = CYAN

CC_NUM0 = 7  # Volume CC number
CC_NUM1 = 10 # Pan CC number
CC_NUM2 = 1  # Modulation Wheel CC number

mode_text = [f"CC #{CC_NUM0}", f"CC #{CC_NUM1}", f"CC #{CC_NUM2}"]
cc_values = [0, 0, 0]  # Initial CCc values

# create the macropad object, rotate orientation
macropad = MacroPad(rotation=0)
macropad.display.auto_refresh = False  # avoid lag
config_mode = 1  # state for startup config

# --- Pixel setup --- #
macropad.pixels.brightness = 0.05
macropad.pixels[0] = YELLOW
macropad.pixels[2] = MAGENTA

# --- Display text setup --- #
text_lines = macropad.display_text("Choose MacroPad mode:")
text_lines[0].text = "Yellow = NumPad"
text_lines[1].text = "Magenta = BlackBox"
text_lines.show()

# --- Character setup --- #
encoder_map = ["+", "-", "*", "/", "(", ")", "%", "<-", ".", "="]

key_map = []

def key_maps(map):
    key_map = [['7', '8', '9',
                    '4', '5', '6',
                    '1', '2', '3',
                    ',', '0', 'Enter'],
                   [40, 41, 42, 43,
                    44, 45, 46, 47,
                    48, 49, 50, 51]]
    return key_map[map]

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

button_mode = 0  # button_mode 0 for NumPad / button_mode 1 for BlackBox

encoder_pos = 0
encoder_mode = 0

characters_entered = ""


def set_button_mode(button_layout):
    global button_mode
    global key_map
    global macropad

    if button_layout == 0:
        button_mode = 0
        key_map = key_maps(0)
    elif button_layout == 1:
        button_mode = 1
        key_map = key_maps(1)


def send_keypad_click(key):
    return macropad.keyboard.send(keycode[key])


def send_encoder_click(encoder_pos):
    if encoder_pos in  [4, 5, 6]:
        return macropad.keyboard.press(macropad.Keycode.SHIFT, encoder_keycode[encoder_pos]), macropad.keyboard.release_all()
    else:
        return macropad.keyboard.send(encoder_keycode[encoder_pos])


def config_checkt(key_event):
    global config_mode
    global BKG_COLOR
    global PRESSED_COLOR

    if key_event.pressed:
        if key_event.key_number == 0:
            set_button_mode(0)
            config_mode = 0
            BKG_COLOR = YELLOW
            PRESSED_COLOR = WHITE
            macropad.pixels.brightness = 0.05
            set_pixel_colors()
        if key_event.key_number == 2:
            set_button_mode(1)
            config_mode = 0
            BKG_COLOR = MAGENTA
            PRESSED_COLOR = CYAN
            macropad.pixels.brightness = 0.05
            set_pixel_colors()


def set_pixel_colors():
    for key in range(12):
        if key == 9 and button_mode == 0:
            macropad.pixels[key] = CYAN
        elif key == 11 and button_mode == 0:
            macropad.pixels[key] = MAGENTA
        else:
            macropad.pixels[key] = BKG_COLOR


def reset_pixel_to_color_a(key):
    if key == 9 and button_mode == 0:
        macropad.pixels[key] = CYAN
    elif key == 11 and button_mode == 0:
        macropad.pixels[key] = MAGENTA
    else:
        macropad.pixels[key] = BKG_COLOR


last_knob_pos = macropad.encoder  # store knob position state

while True:
    if macropad.keys.events:  # check for key press or release
        text_lines.show()
        key_event = macropad.keys.events.get()
        if config_mode == 1:
            config_checkt(key_event)
            if button_mode == 0:
                text_lines = macropad.display_text("NumPad")
                text_lines[0].text = f"Rule of Arithmetic: {encoder_map[encoder_pos]}"
                text_lines.show()
            if button_mode == 1:
                text_lines = macropad.display_text("BlackBox")
                text_lines[0].text = "MIDI"
                text_lines.show()

        elif key_event:
            if button_mode == 0:
                if key_event.pressed:
                    key = key_event.key_number
                    macropad.pixels[key] = PRESSED_COLOR
                    if key_map[key] != "Enter":
                        send_keypad_click(key)
                        characters_entered = f"{characters_entered}{key_map[key]}"
                        text_lines[1].text = f"{characters_entered}"
                    if key_map[key] == "Enter":
                        send_keypad_click(key)
                        characters_entered = ""
                    print(f"{key_map[key]}")
                if key_event.released:
                    key = key_event.key_number
                    reset_pixel_to_color_a(key)

            if button_mode == 1:
                if key_event.pressed:
                    key = key_event.key_number
                    macropad.midi.send(macropad.NoteOn(key_map[key], 120))  # send midi noteon
                    macropad.pixels[key] = PRESSED_COLOR
                    text_lines[1].text = f"SampleOn:{key_map[key]}"
                    print(f"SampleOn:{key_map[key]}")
                if key_event.released:
                    key = key_event.key_number
                    macropad.midi.send(macropad.NoteOff(key_map[key], 0))
                    reset_pixel_to_color_a(key)
                    text_lines[1].text = ""
                    #text_lines[1].text = "SampleOff:{}".format(key_map[key])
                    print(f"SampleOff:{key_map[key]}")

    macropad.encoder_switch_debounced.update()  # check the knob switch for press or release

    if macropad.encoder_switch_debounced.pressed:
        if button_mode == 0:
            send_encoder_click(encoder_pos)
            if encoder_map[encoder_pos] == "<-":
            	characters_entered = characters_entered[:-1]
            else:
                characters_entered = f"{characters_entered}{encoder_map[encoder_pos]}"
            text_lines[1].text = f"{characters_entered}"
            print(f"{encoder_map[encoder_pos]}")
        if button_mode == 1:
            encoder_mode = (encoder_mode+1) % 3
            text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"
        macropad.red_led = macropad.encoder_switch

    if macropad.encoder_switch_debounced.released:
        macropad.red_led = macropad.encoder_switch

    if last_knob_pos is not macropad.encoder:  # knob has been turned
        knob_pos = macropad.encoder  # read encoder
        knob_delta = knob_pos - last_knob_pos  # compute knob_delta since last read
        last_knob_pos = knob_pos  # save new reading
        encoder_pos = last_knob_pos % 10

        if button_mode == 0:
            text_lines[0].text = f"Rule of Arithmetic: {encoder_map[encoder_pos]}"

        elif button_mode == 1:
            if encoder_mode == 0:
                cc_values[encoder_mode] = min(max(cc_values[encoder_mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM0, int(cc_values[encoder_mode]*4.1)))
                text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"
            elif encoder_mode == 1:
                cc_values[encoder_mode] = min(max(cc_values[encoder_mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM1, int(cc_values[encoder_mode]*4.1)))
                text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"
            elif encoder_mode == 2:
                cc_values[encoder_mode] = min(max(cc_values[encoder_mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM2, int(cc_values[encoder_mode]*4.1)))
                text_lines[0].text = f"{mode_text[encoder_mode]} {int(cc_values[encoder_mode]*4.1)}"
        last_knob_pos = macropad.encoder

    text_lines.show()
    macropad.display.refresh()
