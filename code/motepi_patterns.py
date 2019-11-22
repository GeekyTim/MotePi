import math
import queue
import threading
import time
from colorsys import hsv_to_rgb
from subprocess import check_call

import motephat as MotePi

'''
{"mqttmessage": {
            "device": "code",
            "version": 1,
            "payload": {
				"command": "bilgetank",
				"params": {"test":"test"}}}
        }
'''

top_s50 = [50, 50, 50, 50,
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

bottom_s50 = [0, 0, 0, 0,
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

h2s50 = [50, 50, 50, 50,
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

h1s50 = [0, 0, 0, 0,
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

police = [(all50, [0, 0, 255], 0.5),
          (all50, [255, 0, 0], 0.5)]


class MQTTHandler(threading.Thread):

    def __init__(self, q, loop_time=1.0 / 60):
        MotePi.configure_channel(1, 16, False)
        MotePi.configure_channel(2, 16, False)
        MotePi.configure_channel(3, 16, False)
        MotePi.configure_channel(4, 16, False)
        MotePi.set_clear_on_exit(True)
        MotePi.clear()
        MotePi.show()

        self.__queue = q
        self.__qtimeout = loop_time

        self.__command = ""
        self.__motepifunction = 0
        self.__params = {}
        self.__initial = True  # Is this the first time in this pattern?
        self.__tempvalues = {}  # A dict of values to use between calls to a pattern function
        self.__delay = 0.01  # Default delay

        super(MQTTHandler, self).__init__()

    # An external thread can put a message on a queue for this thread to process
    def onthread(self, function, *args, **kwargs):
        self.__queue.put((function, args, kwargs))

    def run(self):
        while True:
            try:
                command, args, kwargs = self.__queue.get(timeout=self.__qtimeout)
                func = getattr(MQTTHandler, command.lower())
                self.__command = command.lower()
                self.__motepifunction = func
                print("args", args[0])
                self.__params = args[0]
                print("Done args")
                print(self.__params)
                self.__initial = True
            except queue.Empty:
                self.idle()
            except AttributeError:
                pass
            except:
                pass

    def idle(self):
        sleeptime = 0.5
        if self.__command != "":
            try:
                self.__motepifunction(self)
                sleeptime = self.__delay
            except:
                pass

        MotePi.show()
        time.sleep(sleeptime)

    # -----------------------------------------------------------------------------------------------------------------------
    # The Mote patterns are below here
    # -----------------------------------------------------------------------------------------------------------------------

    # Runs a defined pattern - one of:
    #
    def runpattern(self, patternset):
        for pattern in patternset:
            matrix = pattern[0]
            colour = pattern[1]
            pause = pattern[2]
            # print (matrix, colour, pause)

            if len(matrix) == 1:
                setMatrixToColour(colour, matrix[0] / 100.0)
            else:
                drawMatrix(matrix, colour)
            time.sleep(pause)

    # Sets the Mote all to one colour
    def setmatrixtocolour(self, colour, brightness):
        MotePi.set_all(colour[0], colour[1], colour[2], brightness=brightness)

    # Draws the matrix pattern on the Mote with the matrix setting the brightness of each
    # pixel and colour setting the colour
    def drawmatrix(self, matrix, colour):
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

            # print(channel, index, r, g, b, brightness)

            MotePi.set_pixel(channel + 1, index, r, g, b, brightness=brightness)

    # The Pimoroni 'Bilgetank' pattern
    def bilgetank(self):
        if self.__initial:
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

                MotePi.set_pixel(channel, pixel, r, g, b)

                self.__tempvalues["phase"] = self.__tempvalues["phase"] + 1

    # Pulses white in and out
    def pulsewhite(self):
        if self.__initial:
            self.__tempvalues = {}
            self.__delay = 0.01
            self.__initial = False

        br = (math.sin(time.time()) + 1) / 2
        br *= 255.0
        br = int(br)

        for channel in range(1, 5):
            for pixel in range(16):
                MotePi.set_pixel(channel, pixel, br, br, br)

    # Pimoroni sample - Pastel colours
    def pastels(self):
        if self.__initial:
            self.__tempvalues = {"offset": 0}
            self.__delay = 0.01
            self.__initial = False

        self.__tempvalues["offset"] = self.__tempvalues["offset"] + 1
        for channel in range(4):
            for pixel in range(16):
                hue = self.__tempvalues["offset"] + (10 * (channel * 16) + pixel)
                hue %= 360
                hue /= 360.0

                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue, 1.0, 1.0)]
                MotePi.set_pixel(channel + 1, pixel, r, g, b)

    # Pimoroni Rainbow sample
    def rainbow(self):
        if self.__initial:
            self.__tempvalues = {}
            self.__delay = 0.01
            self.__initial = False

        h = time.time() * 50
        for channel in range(4):
            for pixel in range(16):
                hue = (h + (channel * 64) + (pixel * 4)) % 360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue / 360.0, 1.0, 1.0)]
                MotePi.set_pixel(channel + 1, pixel, r, g, b)

    # Turns the Pi off
    def turnoff(self):
        if "status" in self.__params:
            print("It's a turn off")
            if self.__params["status"].lower() == "off":
                MotePi.clear()
                MotePi.show()
                check_call(['sudo', 'poweroff'])
