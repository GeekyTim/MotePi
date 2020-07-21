import math
import os
import threading
import time

import motephat as MotePi
from colorsys import hsv_to_rgb

'''
{"mqttmessage": {
            "device": "MotePi",
            "version": 1,
            "payload": {
				"command": "bilgetank",
				"params": {"test":"test"}}}
        }
'''


# Handles the contents of a single queue
class MotePiPatterns(threading.Thread):
    """ Draw the patterns on the Mote strips """
    __top_s50 = [50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 50, 50, 50, 50,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0,
                 0, 0, 0, 0]

    __bottom_s50 = [0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    0, 0, 0, 0,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50,
                    50, 50, 50, 50]

    __h2s50 = [50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0]

    __h1s50 = [0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50,
               0, 0, 0, 0,
               50, 50, 50, 50]

    all50 = [50]

    __police = [(all50, [0, 0, 255], 0.5),
                (all50, [255, 0, 0], 0.5)]

    def __init__(self):
        """ Initialise the Mote """
        MotePi.configure_channel(1, 16, False)
        MotePi.configure_channel(2, 16, False)
        MotePi.configure_channel(3, 16, False)
        MotePi.configure_channel(4, 16, False)
        MotePi.set_clear_on_exit(True)
        self.__clearall()

        self.__command = "nothing"
        self.__params = {}
        self.__lastcommand = "nothing"
        self.__initial = True  # Is this the first time in this pattern?
        self.__tempvalues = {}  # A dict of values to use between calls to a pattern function
        self.__delay = 0.01  # Default delay

        super(MotePiPatterns, self).__init__()

    def run(self):
        ''' Loop around, fetching the contents of the MQTT messages '''
        while True:
            try:
                self.redirection()
            except:
                print("Error in the animation")
            finally:
                self.idle()

    def idle(self):
        sleeptime = 0.5
        if self.__command != "":
            sleeptime = self.__delay
            MotePi.show()
        time.sleep(sleeptime)

    def messagehandler(self, command, params):
        """ MQTT will call this method to handle the message """
        command = command.lower()

        if command != self.__lastcommand:
            self.__initial = True
            self.__command = command
            self.__params = params

    def redirection(self):
        if self.__command != "":
            if self.__command == "police":
                self.__police()
            elif self.__command == "bilgetank":
                self.__bilgetank()
            elif self.__command == "matrix":
                self.__matrix()
            elif self.__command == "pastels":
                self.__pastels()
            elif self.__command == "pulsewhite":
                self.__pulsewhite()
            elif self.__command == "rainbow":
                self.__rainbow()
            elif self.__command == "power":
                self.__power(self.__params)

    # -----------------------------------------------------------------------------------------------------------------------
    # The Mote patterns are below here
    # -----------------------------------------------------------------------------------------------------------------------

    def __clearall(self):
        # MotePi.set_all(0, 0, 0)
        self.__setbrighness(1.0)
        MotePi.clear()
        MotePi.show()

    def __runpattern(self, patternset):
        for pattern in patternset:
            matrix = pattern[0]
            colour = pattern[1]
            pause = pattern[2]

            if len(matrix) == 1:
                self.__setmatrixtocolour(colour, matrix[0] / 100.0)
            else:
                self.__drawmatrix(matrix, colour)
            time.sleep(pause)

    # Sets the Mote all to one colour
    def __setmatrixtocolour(self, colour, brightness):
        MotePi.set_all(colour[0], colour[1], colour[2], brightness=brightness)

    # Draws the matrix pattern on the Mote with the matrix setting the brightness of each
    # pixel and colour setting the colour
    def __drawmatrix(self, matrix, colour):
        count = len(matrix)
        red, green, blue = colour[0], colour[1], colour[2]
        for matrixelement in range(0, count):
            index, channel = divmod(matrixelement, 4)
            brightness = matrix[matrixelement] / 100.0

            if brightness > 0.0:
                r = red
                g = green
                b = blue
            else:
                r, g, b = 0, 0, 0

            MotePi.set_pixel(channel + 1, index, r, g, b, brightness=brightness)

    def __setbrighness(selfself, brightness):
        for channel in [1, 2, 3, 4]:
            for pixel in range(16):
                MotePi.set_pixel(channel, pixel, 0, 0, 0, brightness=brightness)
        MotePi.show()

    # Police
    def __police(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {"colour": "blue", "time": time.time()}
            self.__delay = 0.05
            self.__drawmatrix(self.__top_s50, [255, 0, 0])
            self.__initial = False

        if (time.time() - self.__tempvalues["time"]) > 0.5:
            if self.__tempvalues["colour"] == "blue":
                self.__tempvalues = {"colour": "red", "time": time.time()}
                self.__drawmatrix(self.__top_s50, [255, 0, 0])
            else:
                self.__tempvalues = {"colour": "blue", "time": time.time()}
                self.__drawmatrix(self.__bottom_s50, [0, 0, 255])

    def __matrix(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {"start": [5, 0, 4, 13], "length": [5, 9, 3, 5]}
            self.__delay = 0.2
            self.__initial = False

        for channel in [1, 2, 3, 4]:
            for pixel in range(16):
                green = 0.1 + 0.9 * (
                        (pixel - self.__tempvalues["start"][channel - 1]) / (
                            self.__tempvalues["length"][channel - 1] - 1))
                if 0 > green or green > 1:
                    green = 0
                else:
                    green = 255 * (1.0 - green)

                MotePi.set_pixel(channel, pixel, 0, green, 0, brightness=0.2)
            self.__tempvalues["start"][channel - 1] = (self.__tempvalues["start"][channel - 1] - 1) % 16

    # The Pimoroni 'Bilgetank' pattern
    def __bilgetank(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {"phase": 0}
            self.__delay = 0.01
            self.__initial = False

        hue_start = 160
        hue_range = 80
        speed = 1

        for channel in [1, 2, 3, 4]:
            for pixel in range(MotePi.get_pixel_count(channel)):
                h = (time.time() * speed) + (self.__tempvalues["phase"] / 10.0)

                h = math.sin(h) * (hue_range / 2)
                hue = hue_start + (hue_range / 2) + h
                hue %= 360

                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue / 360.0, 1.0, 1.0)]

                MotePi.set_pixel(channel, pixel, r, g, b, 1.0)

                self.__tempvalues["phase"] = self.__tempvalues["phase"] + 1

    # Pulses white in and out
    def __pulsewhite(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {"shade": 0, "difference": 5}
            self.__delay = 0.1
            self.__initial = False

        # br = (math.sin(time.time()) + 1) / 2
        # br *= 255.0
        # br = int(br)
        br = self.__tempvalues["shade"] + self.__tempvalues["difference"]
        if br > 255.0 or br < 0.0:
            self.__tempvalues["difference"] = -self.__tempvalues["difference"]
            br = br + self.__tempvalues["difference"]

        for channel in [1, 2, 3, 4]:
            for pixel in range(16):
                MotePi.set_pixel(channel, pixel, br, br, br, 1.0)

        self.__tempvalues = {"shade": br, "difference": self.__tempvalues["difference"]}

    # Pimoroni sample - Pastel colours
    def __pastels(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {"offset": 0}
            self.__delay = 0.01
            self.__initial = False

        self.__tempvalues["offset"] = self.__tempvalues["offset"] + 1

        for channel in [1, 2, 3, 4]:
            for pixel in range(16):
                hue = self.__tempvalues["offset"] + (10 * ((channel - 1) * 16) + pixel)
                hue %= 360
                hue /= 360.0

                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                MotePi.set_pixel(channel, pixel, r, g, b, 1.0)

    # Pimoroni Rainbow sample
    def __rainbow(self):
        if self.__initial:
            self.__clearall()
            self.__tempvalues = {}
            self.__delay = 0.01
            self.__initial = False

        h = time.time() * 50
        for channel in [1, 2, 3, 4]:
            for pixel in range(16):
                hue = (h + ((channel - 1) * 64) + (pixel * 4)) % 360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue / 360.0, 1.0, 1.0)]
                MotePi.set_pixel(channel, pixel, r, g, b, 1.0)

    # Turns the Pi off
    def __power(self, params):
        if "action" in params:
            self.__clearall()
            if params["action"].lower() == "off":
                os.system('sudo shutdown -h now')
            elif params["action"].lower() == "reboot":
                os.system('sudo reboot now')
