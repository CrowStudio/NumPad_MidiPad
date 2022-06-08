#                             NumPad_MidiPad
#    Copyright 2022 Daniel Arvidsson <daniel.arvidsson@crowstudio.se>
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
import time
import gc

YELLOW = (230, 100, 0)
MAGENTA = (255, 0, 255)

SCREEN_ACTIVE = 10

# create the macropad object, rotation none
macropad = MacroPad(rotation=0)
macropad.display.auto_refresh = False  # avoid lag

def configure_keypad():
    global text_lines
    global button_mode

    if key_event.key_number == 0:
        from NumPad import NumPad
        button_mode = "NumPad"
        keypad = NumPad(macropad)
        keypad.set_pixel_color_mode()
        text_lines = set_button_mode_text(keypad)
    elif key_event.key_number == 2:
        from MidiCtrl import MidiCtrl
        button_mode = "MidiCtrl"
        keypad = MidiCtrl(macropad)
        keypad.set_pixel_color_mode()
        keypad.key_map = keypad.key_maps[0]
        keypad.init_row = False
        text_lines = set_button_mode_text(keypad)
    return keypad


def set_button_mode_text(keypad):
    if button_mode == "NumPad":
        text_lines = macropad.display_text("NumPad")
        text_lines[0].text = f"Encoder character: {keypad.ENCODER_MAP[keypad.encoder_pos]}"
    elif button_mode == "MidiCtrl":
        text_lines = macropad.display_text("BlackBox MIDI")
        text_lines[0].text = f"{keypad.MODE_TEXT[keypad.encoder_mode]} {keypad.row[keypad.row_pos]}"
    return text_lines


def check_for_screensaver():
    if loop_time - time_of_last_action <= SCREEN_ACTIVE:
        return False
    keypad.macropad.pixels.brightness = 0
    blank_display.show()
    return True


def deactivate_screensaver():
    keypad.macropad.pixels.brightness = 0.05
    keypad.last_knob_pos = keypad.macropad.encoder
    text_lines.show()
    return loop_time


# --- Start-up image --- #
macropad.display_image("img/CrowStudio_logo.bmp")
time.sleep(3)

# --- Display text setup --- #
blank_display = macropad.display_text("") # for screen saver
text_lines = macropad.display_text("Choose MacroPad mode:")
text_lines[0].text = "Yellow = NumPad"
text_lines[1].text = "Magenta = BlackBox"
text_lines.show()
macropad.display.refresh()

# --- Pixel setup --- #
macropad.pixels.brightness = 0.05
macropad.pixels[0] = YELLOW
macropad.pixels[2] = MAGENTA

button_mode = "INIT"

while button_mode == "INIT":
    if macropad.keys.events:
        key_event = macropad.keys.events.get()
        keypad = configure_keypad()

macropad.display.refresh()

gc.collect()
print(f"Free mem after configure_keypad(): {gc.mem_free()}")

time_of_last_action = loop_time = time.monotonic()

while True:
    loop_time = time.monotonic()
    text_lines.show()

    if keypad.macropad.keys.events:  # check for key press or release
        key_event = keypad.macropad.keys.events.get()
        if key_event.pressed and not keypad.macropad_sleep:
            time_of_last_action = keypad.send_key_press(key_event, text_lines)
        elif key_event.released and not keypad.macropad_sleep:
            time_of_last_action = keypad.key_release(key_event, text_lines)
        elif key_event.released:
            time_of_last_action = deactivate_screensaver()

    if keypad.last_knob_pos is not keypad.macropad.encoder:
        if keypad.macropad_sleep:
            time_of_last_action = deactivate_screensaver()
        else:
            time_of_last_action = keypad.read_knob_value(text_lines)

    keypad.macropad.encoder_switch_debounced.update() # check the knob switch for press or release

    if keypad.macropad.encoder_switch_debounced.pressed and keypad.macropad_sleep:
        time_of_last_action = deactivate_screensaver()

    elif keypad.macropad.encoder_switch_debounced.pressed:
        time_of_last_action = keypad.handle_encoder_click(text_lines)
        keypad.macropad.red_led = keypad.macropad.encoder_switch

    elif keypad.macropad.encoder_switch_debounced.released:
        keypad.macropad.red_led = keypad.macropad.encoder_switch

    if keypad.clear_screen: # only used for NumPad
        keypad.clear_entered_characters(time_of_last_action, text_lines)
    keypad.macropad_sleep = check_for_screensaver()
    macropad.display.refresh()