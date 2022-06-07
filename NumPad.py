from adafruit_macropad import MacroPad
import time

class NumPad:
    def __init__(self, macropad):
        self.YELLOW = (230, 100, 0)
        self.WHITE = (255, 255, 255)
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)

        self.NUMPAD_KEY_COLOR = [self.YELLOW, self.YELLOW, self.YELLOW,
                                 self.YELLOW, self.YELLOW, self.YELLOW,
                                 self.YELLOW, self.YELLOW, self.YELLOW,
                                 self.CYAN,   self.YELLOW, self.MAGENTA]

        self.PRESSED_COLOR = self.WHITE

        self.macropad = macropad
        self.encoder_map = ["+", "-", "*", "/", "(", ")", "%", "<-", ".", "="]

        self.RESET_ENTERED_CHAR = 3

        self.key_map = ['7', '8', '9',
                        '4', '5', '6',
                        '1', '2', '3',
                        ',', '0', 'Enter']
                    
        self.keycode = [self.macropad.Keycode.KEYPAD_SEVEN,
                self.macropad.Keycode.KEYPAD_EIGHT,
                self.macropad.Keycode.KEYPAD_NINE,
                self.macropad.Keycode.KEYPAD_FOUR,
                self.macropad.Keycode.KEYPAD_FIVE,
                self.macropad.Keycode.KEYPAD_SIX,
                self.macropad.Keycode.KEYPAD_ONE,
                self.macropad.Keycode.KEYPAD_TWO,
                self.macropad.Keycode.KEYPAD_THREE,
                self.macropad.Keycode.COMMA,
                self.macropad.Keycode.KEYPAD_ZERO,
                self.macropad.Keycode.KEYPAD_ENTER]

        self.encoder_keycode = [self.macropad.Keycode.KEYPAD_PLUS,
                        self.macropad.Keycode.KEYPAD_MINUS,
                        self.macropad.Keycode.KEYPAD_ASTERISK,
                        self.macropad.Keycode.KEYPAD_FORWARD_SLASH,
                        self.macropad.Keycode.EIGHT,
                        self.macropad.Keycode.NINE,
                        self.macropad.Keycode.FIVE,
                        self.macropad.Keycode.BACKSPACE,
                        self.macropad.Keycode.PERIOD,
                        self.macropad.Keycode.KEYPAD_EQUALS]

        self.last_knob_pos = self.macropad.encoder
        self.encoder_pos = 0
        self.clear_screen = False
        self.characters_entered = ""

    def send_key_press(self, key_event, text_lines):
        key = key_event.key_number
        self.macropad.pixels[key] = self.PRESSED_COLOR
        self.macropad.keyboard.send(self.keycode[key])
        self.__update_screen_characters_entered(key, text_lines)
        return time.monotonic()


    def key_release(self, key_event, text_lines):
        key = key_event.key_number
        self.__reset_pixel_to_bkgnd_color(key)


    def __update_screen_characters_entered(self, key, text_lines):
        if key == "Encoder":
            if self.encoder_map[self.encoder_pos] == "<-":
                self.characters_entered = self.characters_entered[:-1]
            elif self.encoder_map[self.encoder_pos] == "=":
                self.clear_screen = True
                self.characters_entered = f"{self.characters_entered}{self.encoder_map[self.encoder_pos]}"
            else:
                self.characters_entered = f"{self.characters_entered}{self.encoder_map[self.encoder_pos]}"
        elif self.key_map[key] == "Enter":
            self.clear_screen = True
        else:
            self.clear_screen = False
            self.characters_entered = f"{self.characters_entered}{self.key_map[key]}"
        text_lines[1].text = f"{self.characters_entered}"


    def read_knob_value(self, text_lines):
        self.encoder_pos = self.macropad.encoder % 10
        text_lines[0].text = f"Encoder character: {self.encoder_map[self.encoder_pos]}"
        self.last_knob_pos = self.macropad.encoder
        return time.monotonic()


    def handle_encoder_click(self, text_lines):
        self.__update_screen_characters_entered("Encoder", text_lines)
        if self.encoder_pos in [4, 5, 6]:
            self.macropad.keyboard.press(self.macropad.Keycode.SHIFT,
                self.encoder_keycode[self.encoder_pos]), self.macropad.keyboard.release_all()
        else:
            self.macropad.keyboard.send(self.encoder_keycode[self.encoder_pos])
        return time.monotonic()


    def clear_entered_characters(self, time_of_last_action, text_lines):
        self.characters_entered = ""
        if (time.monotonic() - time_of_last_action) > self.RESET_ENTERED_CHAR:
            text_lines[1].text = f"{self.characters_entered}"
            self.clear_screen = False


    def set_pixel_color_mode(self):
        self.macropad.pixels.brightness = 0.05
        for key in range(12):
            self.macropad.pixels[key] = self.NUMPAD_KEY_COLOR[key]


    def __reset_pixel_to_bkgnd_color(self, key):
        self.macropad.pixels[key] = self.NUMPAD_KEY_COLOR[key]