from adafruit_macropad import MacroPad
import time

class MidiCtrl:
    def __init__(self, macropad):
        self.CYAN = (0, 255, 255)
        self.MAGENTA = (255, 0, 255)
        self.MINT = (0, 255, 50)

        self.NUMPAD_KEY_COLOR = self.MAGENTA
        self.PRESSED_COLOR = self.CYAN
        
        self.CC_NUM0 = 7  # Volume
        self.CC_NUM1 = 10  # Pan
        self.CC_NUM2 = 1  # Modulation Wheel

        self.CC = [self.CC_NUM0, self.CC_NUM1, self.CC_NUM2]

        self.macropad = macropad

        self.key_map = []
        
        self.key_maps = [[48, 49, 50,
                        44, 45, 46,
                        40, 41, 42,
                        36, 37, 38],
                        [48, 49, 51,
                         44, 45, 47,
                         40, 41, 43,
                         36, 37, 39]]

        self.row = [3, 4]

        self.last_knob_pos = self.macropad.encoder  # store knob position state

        self.knob_pos = 0
        self.knob_delta = 0
        self.read_diff = 0
        self.encoder_mode = 3
        self.encoder_pos = 0
        self.row_pos = 0
        self.mode_text = [f"CC # {self.CC_NUM0}:", f"CC #{self.CC_NUM1}:",
                          f"CC # {self.CC_NUM2}:", "Active row:"]
        self.cc_values = [0, 0, 0]  # initial CC values

        self.row_4 = False
        
        self.clear_screen = False

    def send_key_press(self, key_event, text_lines):
        key = key_event.key_number
        self.macropad.pixels[key] = self.PRESSED_COLOR
        self.macropad.midi.send(self.macropad.NoteOn(self.key_map[key], 120))
        text_lines[2].text = f"SampleOn:{self.key_map[key]}"
        return time.monotonic()


    def key_release(self, key_event, text_lines):
        key = key_event.key_number
        self.macropad.midi.send(self.macropad.NoteOff(self.key_map[key], 0))
        self.__reset_pixel_to_bkgnd_color(key)
        text_lines[2].text = ""


    def read_knob_value(self, text_lines):
        if self.encoder_mode in [0, 1, 2]:
            self.knob_pos = self.macropad.encoder
            self.knob_delta = self.knob_pos - self.last_knob_pos
            self.cc_values[self.encoder_mode] = min(max(self.cc_values[self.encoder_mode] + self.knob_delta, 0), 127)
            self.__send_cc_value(self.encoder_mode)
            text_lines[0].text = f"{self.mode_text[self.encoder_mode]} {int(self.cc_values[self.encoder_mode])}"
        else:
            self.row_pos = (self.macropad.encoder + self.read_diff) % 2
            self.__toggle_row()
            text_lines[0].text = f"{self.mode_text[self.encoder_mode]} {self.row[self.row_pos]}"
        self.last_knob_pos = self.macropad.encoder
        return time.monotonic()


    def __send_cc_value(self, num):
        self.macropad.midi.send(self.macropad.ControlChange(self.CC[num], int(self.cc_values[self.encoder_mode])))
        

    def handle_encoder_click(self, text_lines):
        self.encoder_mode = (self.encoder_mode + 1) % 4
        if self.encoder_mode in [0, 1, 2]:
            text_lines[0].text = f"{self.mode_text[self.encoder_mode]} {int(self.cc_values[self.encoder_mode])}"
        else:
            text_lines[0].text = f"{self.mode_text[self.encoder_mode]} {self.row[self.row_pos]}"
        return time.monotonic()


    def __toggle_row(self):
        if self.row[self.row_pos] == 3:
            self.row_4 = False
            self.key_map = self.key_maps[0]
        else:
            self.row_4 = True
            self.key_map = self.key_maps[1]
        self.set_pixel_color_mode()


    def set_pixel_color_mode(self):
        self.macropad.pixels.brightness = 0.05
        for key in range(12):
            self.__set_background_colors(key)


    def __set_background_colors(self, key):
        if key in [2, 5, 8, 11] and self.row_4 == True:
            self.macropad.pixels[key] = self.MINT
        else:
           self.macropad.pixels[key] = self.NUMPAD_KEY_COLOR


    def __reset_pixel_to_bkgnd_color(self, key):
        self.__set_background_colors(key)
