from adafruit_macropad import MacroPad
import time

class NumPad:
    YELLOW = (230, 100, 0)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)

    KEY_COLOR = [YELLOW, YELLOW, YELLOW,
                 YELLOW, YELLOW, YELLOW,
                 YELLOW, YELLOW, YELLOW,
                 CYAN,   YELLOW, MAGENTA]

    PRESSED_COLOR = WHITE

    RESET_ENTERED_CHAR = 3

    ZERO = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    COMMA = ','
    ENTER = "Enter"

    KEY_MAP = [SEVEN, EIGHT, NINE,
               FOUR,  FIVE,  SIX,
               ONE,   TWO,   THREE,
               COMMA, ZERO,  ENTER]

    PLUS = '+'
    MINUS = '-'
    TIMES = '*'
    DIVIDE = '/'
    LEFT_PARENTHESIS = '('
    RIGHT_PARENTHESIS = ')'
    PRECENT = '%'
    BACKSPACE = '<-'
    PERIOD = '.'
    EQUALS = '='

    ENCODER_MAP = [PLUS, MINUS, TIMES, DIVIDE, LEFT_PARENTHESIS,
                   RIGHT_PARENTHESIS, PRECENT, BACKSPACE, PERIOD, EQUALS]

    def __init__(self, macropad):
        self.macropad = macropad

        self.KEYCODE = [self.macropad.Keycode.KEYPAD_SEVEN,
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

        self.ENCODER_KEYCODE = [self.macropad.Keycode.KEYPAD_PLUS,
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
        self.macropad.keyboard.send(self.KEYCODE[key])
        self.__update_screen_characters_entered(key, text_lines)
        return time.monotonic()


    def key_release(self, key_event, text_lines):
        key = key_event.key_number
        self.__reset_pixel_to_bkgnd_color(key)


    def __update_screen_characters_entered(self, key, text_lines):
        if key == "Encoder":
            if NumPad.ENCODER_MAP[self.encoder_pos] == '<-':
                self.characters_entered = self.characters_entered[:-1]
            elif NumPad.ENCODER_MAP[self.encoder_pos] == '=':
                self.clear_screen = True
                self.characters_entered = f"{self.characters_entered}{NumPad.ENCODER_MAP[self.encoder_pos]}"
            else:
                self.characters_entered = f"{self.characters_entered}{NumPad.ENCODER_MAP[self.encoder_pos]}"
        elif NumPad.KEY_MAP[key] == "Enter":
            self.clear_screen = True
        else:
            self.clear_screen = False
            self.characters_entered = f"{self.characters_entered}{NumPad.KEY_MAP[key]}"
        text_lines[1].text = f"{self.characters_entered}"


    def read_knob_value(self, text_lines):
        self.encoder_pos = self.macropad.encoder % 10
        text_lines[0].text = f"Encoder character: {NumPad.ENCODER_MAP[self.encoder_pos]}"
        self.last_knob_pos = self.macropad.encoder
        return time.monotonic()


    def handle_encoder_click(self, text_lines):
        self.__update_screen_characters_entered("Encoder", text_lines)
        if self.encoder_pos in [4, 5, 6]:
            self.macropad.keyboard.press(self.macropad.Keycode.SHIFT,
                self.ENCODER_KEYCODE[self.encoder_pos]), self.macropad.keyboard.release_all()
        else:
            self.macropad.keyboard.send(self.ENCODER_KEYCODE[self.encoder_pos])
        return time.monotonic()


    def clear_entered_characters(self, time_of_last_action, text_lines):
        self.characters_entered = ""
        if (time.monotonic() - time_of_last_action) > NumPad.RESET_ENTERED_CHAR:
            text_lines[1].text = f"{self.characters_entered}"
            self.clear_screen = False


    def set_pixel_color_mode(self):
        self.macropad.pixels.brightness = 0.05
        for key in range(12):
            self.macropad.pixels[key] = NumPad.KEY_COLOR[key]


    def __reset_pixel_to_bkgnd_color(self, key):
        self.macropad.pixels[key] = NumPad.KEY_COLOR[key]