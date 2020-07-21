#!/usr/bin/env python3

from signal import pause

import mqtt_messages
import motepi_patterns as mqtt_handler


def main():
    # Set up the handler class
    handlerclass = mqtt_handler.MotePiPatterns()
    # Start MQTT Listener
    mqtt_messages.Messages(handlerclass)

    handlerclass.start()

    pause()

if __name__ == "__main__":
    main()

print("MotePi: Shouldn't get here!")
