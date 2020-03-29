#!/usr/bin/env python3

import motepi_patterns as mqtt_handler
import mqtt_config
import mqtt_messages
from signal import pause


def main():
    mqtthandle = mqtt_messages.Messages(mqtt_config)

    handlerclass = mqtt_handler.MotePiPatterns(mqtthandle, "MoteControl")
    handlerclass.start()

    pause()


if __name__ == "__main__":
    main()

print("MotePi: Shouldn't get here!")
