from adafruit_macropad import MacroPad
import time

class Sample:
    TOGGLE = "Toggle"
    MOM = "Gate/Trig"
    OFF = "OFF"
    ON = "ON"

class CC:
    MIN = 0
    MAX = 127

    NUM_0 = 7  # Volume
    NUM_1 = 10 # Pan
    NUM_2 = 1  # Modulation Wheel

    NUM_LIST = [NUM_0, NUM_1, NUM_2]

class MidiCtrl:
    CYAN = (0, 255, 255)
    MAGENTA = (255, 0, 255)
    MINT = (0, 255, 50)

    KEY_COLOR = MAGENTA
    PRESSED_COLOR = CYAN

    VELOCITY = 120

    MODE_TEXT = [f"CC # {CC.NUM_0}:", f"CC #{CC.NUM_1}:",
                 f"CC # {CC.NUM_2}:", "Set Toggle mode",
                 "Active row:"]

    def __init__(self, macropad):
        self.macropad = macropad
        self.macropad_sleep = False

        self.key_map = []

        self.key_maps = [[48, 49, 50,
                          44, 45, 46,
                          40, 41, 42,
                          36, 37, 38],
                         [48, 49, 51,
                          44, 45, 47,
                          40, 41, 43,
                          36, 37, 39]]

        self.latch_map = {0: [Sample.MOM, Sample.OFF],  1: [Sample.MOM, Sample.OFF],  2: [Sample.MOM, Sample.OFF],
                          3: [Sample.MOM, Sample.OFF],  4: [Sample.MOM, Sample.OFF],  5: [Sample.MOM, Sample.OFF],
                          6: [Sample.MOM, Sample.OFF],  7: [Sample.MOM, Sample.OFF],  8: [Sample.MOM, Sample.OFF],
                          9: [Sample.MOM, Sample.OFF], 10: [Sample.MOM, Sample.OFF], 11: [Sample.MOM, Sample.OFF]}

        self.latch_row_3 = {2: [Sample.MOM, Sample.OFF],
                            5: [Sample.MOM, Sample.OFF],
                            8: [Sample.MOM, Sample.OFF],
                           11: [Sample.MOM, Sample.OFF]}

        self.latch_row_4 = {2: [Sample.MOM, Sample.OFF],
                            5: [Sample.MOM, Sample.OFF],
                            8: [Sample.MOM, Sample.OFF],
                           11: [Sample.MOM, Sample.OFF]}

        self.row = [3, 4]

        self.last_knob_pos = self.macropad.encoder  # store knob position state

        self.knob_pos = 0
        self.knob_delta = 0

        self.row_pos = 0
        self.row_delta = 0

        self.encoder_mode = 4

        self.cc_values = [0, 0, 0]  # initial CC values

        self.init_row = True
        self.row_4 = False

        self.latch_config = False

        self.clear_screen = False

    def send_key_press(self, key_event, text_lines):
        key = key_event.key_number
        if self.latch_config:
            self.__config_toggle_mode(key)
        else:
            self.macropad.pixels[key] = MidiCtrl.PRESSED_COLOR
            self.macropad.midi.send(self.macropad.NoteOn(self.key_map[key], self.VELOCITY))
            text_lines[2].text = f"SampleOn:{self.key_map[key]}"
        return time.monotonic()


    def key_release(self, key_event, text_lines):
        key = key_event.key_number
        if self.latch_config:
            self.macropad.pixels[key] = MidiCtrl.PRESSED_COLOR if self.latch_map[
                key][0] == Sample.TOGGLE else MidiCtrl.KEY_COLOR
        else:
            self.macropad.midi.send(self.macropad.NoteOff(self.key_map[key], 0))
            self.__reset_pixel_to_bkgnd_color(key)
            text_lines[2].text = ""
        return time.monotonic()


    def read_knob_value(self, text_lines):
        if self.encoder_mode in [0, 1, 2]:
            self.__read_cc_value()
            self.__send_cc_value(self.encoder_mode)
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]} {int(self.cc_values[self.encoder_mode])}"
        elif self.encoder_mode == 3:
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]}"
        else:
            self.__toggle_row()
            self.set_pixel_color_mode()
            self.init_row = False
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]} {self.row[self.row_pos]}"
        self.last_knob_pos = self.macropad.encoder
        return time.monotonic()


    def handle_encoder_click(self, text_lines):
        self.encoder_mode = (self.encoder_mode + 1) % 5
        if self.encoder_mode in [0, 1, 2]:
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]} {int(self.cc_values[self.encoder_mode])}"
        elif self.encoder_mode == 3:
            self.latch_config = True
            self.__show_toggle_pixel_status()
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]}"
        else:
            self.latch_config = False
            self.__restore_pixel_status()
            text_lines[0].text = f"{MidiCtrl.MODE_TEXT[self.encoder_mode]} {self.row[self.row_pos]}"
        return time.monotonic()


    def set_pixel_color_mode(self):
        self.macropad.pixels.brightness = 0.05
        for key in range(12):
            self.__set_background_colors(key)


    def __read_cc_value(self):
        self.knob_delta = self.macropad.encoder - self.last_knob_pos
        self.cc_values[self.encoder_mode] = min(
            max(self.cc_values[self.encoder_mode] + self.knob_delta, CC.MIN), CC.MAX)


    def __send_cc_value(self, x):
        self.macropad.midi.send(self.macropad.ControlChange(
            CC.NUM_LIST[x], int(self.cc_values[self.encoder_mode])))


    def __toggle_row(self):
        self.row_delta = self.row_pos - self.last_knob_pos
        self.row_pos = (self.macropad.encoder + self.row_delta) % 2
        if self.row[self.row_pos] == 3:
            self.row_4 = False
            self.key_map = self.key_maps[0]
        else:
            self.row_4 = True
            self.key_map = self.key_maps[1]
        self.init_row = True
        self.__toggle_latch_row()


    def __toggle_latch_row(self):
        for key in self.latch_map:
            if key in [2, 5, 8, 11]:
                if self.row_4 == True:
                    self.latch_row_3[key] = self.latch_map[key]
                    self.latch_map[key] = self.latch_row_4[key]

                elif self.row_4 == False:
                    self.latch_row_4[key] = self.latch_map[key]
                    self.latch_map[key] = self.latch_row_3[key]


    def __set_background_colors(self, key):
        if key in [2, 5, 8, 11] and self.row_4 == True:
            self.__check_toggle_state(key, MidiCtrl.MINT)
        else:
           self.__check_toggle_state(key, MidiCtrl.KEY_COLOR)


    def __reset_pixel_to_bkgnd_color(self, key):
        self.__set_background_colors(key)


    def __check_toggle_state(self, key, COLOR):
        if self.init_row == True:
            if self.latch_map[key][0] == Sample.TOGGLE and self.latch_map[key][1] == Sample.ON:
                self.macropad.pixels[key] = MidiCtrl.PRESSED_COLOR
            else:
                self.macropad.pixels[key] = COLOR
        elif self.latch_map[key][0] == Sample.TOGGLE and self.latch_map[key][1] == Sample.OFF:
            self.latch_map[key][1] = Sample.ON
        elif self.latch_map[key][1] == Sample.ON:
            self.latch_map[key][1] = Sample.OFF
            self.macropad.pixels[key] = COLOR
        else:
            self.macropad.pixels[key] = COLOR


    def __config_toggle_mode(self, key):
        self.latch_map[key][0] = Sample.TOGGLE if self.latch_map[key][0] == Sample.MOM else Sample.MOM

    def __show_toggle_pixel_status(self):
        for key in range(12):
            if key in [2, 5, 8, 11] and self.row_4 == True:
                self.macropad.pixels[key] = MidiCtrl.PRESSED_COLOR if self.latch_map[
                    key][0] == Sample.TOGGLE else MidiCtrl.MINT
            else:
                self.macropad.pixels[key] = MidiCtrl.PRESSED_COLOR if self.latch_map[
                    key][0] == Sample.TOGGLE else MidiCtrl.KEY_COLOR


    def __restore_pixel_status(self):
        self.init_row = True
        self.set_pixel_color_mode()
        self.init_row = False
