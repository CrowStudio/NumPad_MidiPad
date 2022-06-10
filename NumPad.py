from adafruit_macropad import MacroPad
import time

class NumPad:
    YELLOW = (230, 100, 0)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    RED = (255, 0, 0)

    KEY_COLOR = [YELLOW, YELLOW, YELLOW,
                 YELLOW, YELLOW, YELLOW,
                 YELLOW, YELLOW, YELLOW,
                 CYAN,   YELLOW, MAGENTA]

    PRESSED_COLOR = WHITE

    RESET_ENTERED_CHAR = 3

    MODE_TEXT = ["CYAN character:", "Volume:"]

    COMMA = ','
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

    ENCODER_MAP = [COMMA, PLUS, MINUS, TIMES, DIVIDE, LEFT_PARENTHESIS,
                   RIGHT_PARENTHESIS, PRECENT, BACKSPACE, PERIOD, EQUALS]

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
    ENTER = "Enter"

    char = ','

    key_map = [SEVEN, EIGHT, NINE,
               FOUR,  FIVE,  SIX,
               ONE,   TWO,   THREE,
               char,  ZERO,  ENTER]

    def __init__(self, macropad):
        self.macropad = macropad
        self.macropad_sleep = False

        self.ENCODER_KEYCODE = [self.macropad.Keycode.COMMA,
                                self.macropad.Keycode.KEYPAD_PLUS,
                                self.macropad.Keycode.KEYPAD_MINUS,
                                self.macropad.Keycode.KEYPAD_ASTERISK,
                                self.macropad.Keycode.KEYPAD_FORWARD_SLASH,
                                self.macropad.Keycode.EIGHT,
                                self.macropad.Keycode.NINE,
                                self.macropad.Keycode.FIVE,
                                self.macropad.Keycode.BACKSPACE,
                                self.macropad.Keycode.PERIOD,
                                self.macropad.Keycode.KEYPAD_EQUALS]

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

        self.last_knob_pos = self.macropad.encoder
        self.knob_delta = 0
        self.char_pos = 0
        self.volume_direction = 0

        self.level = 0

        self.encoder_mode = 0

        self.clear_screen = False
        self.characters_entered = ""

    def send_key_press(self, key_event, text_lines):
        key = key_event.key_number
        self.macropad.pixels[key] = NumPad.PRESSED_COLOR
        if self.char_pos in [5, 6, 7]:
            self.macropad.keyboard.press(self.macropad.Keycode.SHIFT,
                                         self.keycode[key]), self.macropad.keyboard.release_all()
        else:
            self.macropad.keyboard.send(self.keycode[key])
        self.__update_screen_characters_entered(key, text_lines)
        return time.monotonic()


    def key_release(self, key_event, text_lines):
        key = key_event.key_number
        self.__reset_pixel_to_bkgnd_color(key)
        return time.monotonic()


    def read_knob_value(self, text_lines):
        if self.encoder_mode == 0:
            self.knob_delta = self.char_pos - self.last_knob_pos
            self.char_pos = (self.macropad.encoder + self.knob_delta) % 11
            self.keycode[9] = self.ENCODER_KEYCODE[self.char_pos]
            NumPad.key_map[9] = NumPad.ENCODER_MAP[self.char_pos]
            self.macropad.pixels[9] = NumPad.RED if NumPad.key_map[9] == '<-' else NumPad.CYAN
            text_lines[0].text = f"CYAN character: {NumPad.ENCODER_MAP[self.char_pos]}"
        self.last_knob_pos = self.macropad.encoder
        return time.monotonic()


    def handle_encoder_click(self, text_lines):
        self.encoder_mode = (self.encoder_mode + 1) % 2 
        if self.encoder_mode == 0:
            text_lines[0].text = f"{NumPad.MODE_TEXT[self.encoder_mode]} {NumPad.ENCODER_MAP[self.char_pos]}"
        else:    
            text_lines[0].text = f"{NumPad.MODE_TEXT[self.encoder_mode]} {self.level}"
        return time.monotonic()


    def set_pixel_color_mode(self):
        self.macropad.pixels.brightness = 0.05
        for key in range(12):
            self.macropad.pixels[key] = NumPad.KEY_COLOR[key]


    def clear_entered_characters(self, time_of_last_action, text_lines):
        self.characters_entered = ""
        if (time.monotonic() - time_of_last_action) > NumPad.RESET_ENTERED_CHAR:
            text_lines[1].text = f"{self.characters_entered}"
            self.clear_screen = False


    def __update_screen_characters_entered(self, key, text_lines):
        if NumPad.key_map[key] == '<-':
            self.characters_entered = self.characters_entered[:-1]
        elif NumPad.key_map[key] == '=':
            self.clear_screen = True
            self.characters_entered = f"{self.characters_entered}{NumPad.ENCODER_MAP[self.char_pos]}"
        elif NumPad.key_map[key] == "Enter":
            self.clear_screen = True
        else:
            self.clear_screen = False
            self.characters_entered = f"{self.characters_entered}{NumPad.key_map[key]}"
        text_lines[1].text = f"{self.characters_entered}"


    def __reset_pixel_to_bkgnd_color(self, key):
        self.macropad.pixels[key] = NumPad.KEY_COLOR[key]