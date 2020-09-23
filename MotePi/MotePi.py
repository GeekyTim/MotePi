#!/usr/bin/env python3

from signal import pause

import MQTTMessages as Messages
import motepi_patterns
import mqtt_config as config


def main():
    # Set up the handler class
    handlerclass = motepi_patterns.MotePiPatterns()
    # Start MQTT Listener
    Messages.MQTTMessages(config.mqttconfig, handlerclass)

    handlerclass.start()

    pause()


if __name__ == "__main__":
    main()
