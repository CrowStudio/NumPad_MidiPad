# SPDX-FileCopyrightText: 2022 John Park for Adafruit Industries
# SPDX-License-Identifier: MIT
# Macropad MIDI Tester
# Play MIDI notes with keys
# Click encoder to switch modes
# Turn encoder to adjust CC, ProgramChange, or PitchBend
from adafruit_macropad import MacroPad
from rainbowio import colorwheel

WHITE = (255, 255, 255)
YELLOW = (230, 100, 0)
CYAN = (0, 255, 255)
MAGENTA = (180, 0, 255)

COLOR_A = MAGENTA
COLOR_B = CYAN

CC_NUM0 = 7  # select your CC number
CC_NUM1 = 10  # select your CC number
CC_NUM2 = 1  # select your CC number

encoder_map = ["+", "-", "*", "/", "(", ")", "%", "<-", ".", "="]

macropad = MacroPad(rotation=0)  # create the macropad object, rotate orientation
macropad.display.auto_refresh = False  # avoid lag

button_mode = 0  # mode 0 for NumPad / mode 1 for BlackBox
config_mode = 1  # state for startup config
key_map = []

arith_pos = 0
mode = 0

characters_entered = ""

# --- MIDI variables ---
mode_text = [f"CC #{CC_NUM0}", f"CC #{CC_NUM1}", f"CC #{CC_NUM2}"]
cc_values = [0, 0, 0]  #initial cc values

# --- Pixel setup --- #
macropad.pixels.brightness = 0.1
macropad.pixels[0] = YELLOW
macropad.pixels[2] = MAGENTA

# --- Display text setup ---
text_lines = macropad.display_text("Choose MacroPad mode:")
text_lines[0].text = "Yellow = NumPad"
text_lines[1].text = "Magenta = BlackBox"
text_lines.show()


def set_button_mode(button_layout):
    global button_mode
    global key_map
    global macropad
    if button_layout == 0:
        button_mode = 0
        key_map = ['7', '8', '9', 
        	    '4', '5', '6', 
        	    '1', '2', '3',
        	    ',', '0', 'Enter']
    elif button_layout == 1:
        button_mode = 1
        key_map = [40, 41, 42, 43,
                    44, 45, 46, 47,
                    48, 49, 50, 51]

def keypad_codes(key):
    if key == 0:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_SEVEN)
    elif key == 1:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_EIGHT)
    elif key == 2:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_NINE)
    elif key == 3:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_FOUR)
    elif key == 4:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_FIVE)
    elif key == 5:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_SIX)
    elif key == 6:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_ONE)
    elif key == 7:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_TWO)
    elif key == 8:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_THREE)
    elif key == 9:
        macropad.keyboard.send(macropad.Keycode.COMMA)
    elif key == 10:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_ZERO)
    elif key == 11:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_ENTER)


def encoder_codes(arith_pos):
    if arith_pos == 0:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_PLUS)
    elif arith_pos == 1:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_MINUS)
    elif arith_pos == 2:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_ASTERISK)
    elif arith_pos == 3:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_FORWARD_SLASH)
    elif arith_pos == 4:
        macropad.keyboard.press(macropad.Keycode.SHIFT, macropad.Keycode.EIGHT)
        macropad.keyboard.release_all()
    elif arith_pos == 5:
        macropad.keyboard.press(macropad.Keycode.SHIFT, macropad.Keycode.NINE)
        macropad.keyboard.release_all()
    elif arith_pos == 6:
        macropad.keyboard.press(macropad.Keycode.SHIFT, macropad.Keycode.FIVE)
        macropad.keyboard.release_all()
    elif arith_pos == 7:
        macropad.keyboard.send(macropad.Keycode.BACKSPACE)
    elif arith_pos == 8:
        macropad.keyboard.send(macropad.Keycode.PERIOD)
    elif arith_pos == 9:
        macropad.keyboard.send(macropad.Keycode.KEYPAD_EQUALS)


def config_checkt(key_event):
    global config_mode
    global COLOR_A
    global COLOR_B
    if key_event.pressed:
        if key_event.key_number == 0:
            set_button_mode(0)
            config_mode = 0
            COLOR_A = YELLOW
            COLOR_B = WHITE
            macropad.pixels.brightness = 0.05
            set_pixel_colors()

        if key_event.key_number == 2:
            set_button_mode(1)
            config_mode = 0
            COLOR_A = MAGENTA
            COLOR_B = CYAN
            macropad.pixels.brightness = 0.05
            set_pixel_colors()

def set_pixel_colors():
    for key in range(12):
        if key == 9 and button_mode == 0:
            macropad.pixels[key] = CYAN
        elif key == 11 and button_mode == 0:
            macropad.pixels[key] = MAGENTA
        else:
            macropad.pixels[key] = COLOR_A


def reset_pixel_to_color_a(key):
    if key == 9 and button_mode == 0:
        macropad.pixels[key] = CYAN
    elif key == 11 and button_mode == 0:
        macropad.pixels[key] = MAGENTA
    else:
        macropad.pixels[key] = COLOR_A

# sourcery skip: merge-comparisons, switch
last_knob_pos = macropad.encoder  # store knob position state

while True:
    while macropad.keys.events:  # check for key press or release
        text_lines.show()
        key_event = macropad.keys.events.get()
        if config_mode == 1:
            config_checkt(key_event)
            if button_mode == 0:
                text_lines = macropad.display_text("NumPad")
                text_lines[0].text = f"Rule of Arithmetic: {encoder_map[arith_pos]}"
                text_lines.show()
            if button_mode == 1:
                text_lines = macropad.display_text("BlackBox")
                text_lines[0].text = "MIDI"
                text_lines.show()

        elif key_event:
            if button_mode == 0:
                if key_event.pressed:
                    key = key_event.key_number
                    macropad.pixels[key] = COLOR_B
                    if key_map[key] != "Enter":
                        keypad_codes(key)
                        characters_entered = f"{characters_entered}{key_map[key]}"
                        text_lines[1].text = f"{characters_entered}"
                    if key_map[key] == "Enter":
                        keypad_codes(key)
                        characters_entered = ""
                    print(f"{key_map[key]}")
                if key_event.released:
                    key = key_event.key_number
                    reset_pixel_to_color_a(key)

            if button_mode == 1:
                if key_event.pressed:
                    key = key_event.key_number
                    macropad.midi.send(macropad.NoteOn(key_map[key], 120))  # send midi noteon
                    macropad.pixels[key] = COLOR_B
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
            encoder_codes(arith_pos)
            characters_entered = f"{characters_entered}{encoder_map[arith_pos]}"
            text_lines[1].text = f"{characters_entered}"
            print(f"{encoder_map[arith_pos]}")

        if button_mode == 1:
            mode = (mode+1) % 3
            text_lines[0].text = f"{mode_text[mode]} {int(cc_values[mode]*4.1)}"
        macropad.red_led = macropad.encoder_switch

    if macropad.encoder_switch_debounced.released:
        macropad.red_led = macropad.encoder_switch

    if last_knob_pos is not macropad.encoder:  # knob has been turned
        knob_pos = macropad.encoder  # read encoder
        knob_delta = knob_pos - last_knob_pos  # compute knob_delta since last read
        last_knob_pos = knob_pos  # save new reading
        arith_pos = last_knob_pos % 10

        if button_mode == 0:
            text_lines[0].text = f"Rule of Arithmetic: {encoder_map[arith_pos]}"

        elif button_mode == 1:
            if mode == 0:
                cc_values[mode] = min(max(cc_values[mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM0, int(cc_values[mode]*4.1)))
                text_lines[0].text = f"{mode_text[mode]} {int(cc_values[mode]*4.1)}"

            elif mode == 1:
                cc_values[mode] = min(max(cc_values[mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM1, int(cc_values[mode]*4.1)))
                text_lines[0].text = f"{mode_text[mode]} {int(cc_values[mode]*4.1)}"

            elif mode == 2:
                cc_values[mode] = min(max(cc_values[mode] + knob_delta, 0), 31)  # scale the value
                macropad.midi.send(macropad.ControlChange(CC_NUM2, int(cc_values[mode]*4.1)))
                text_lines[0].text = f"{mode_text[mode]} {int(cc_values[mode]*4.1)}"

        last_knob_pos = macropad.encoder
    text_lines.show()
    macropad.display.refresh()
