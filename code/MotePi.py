#!/usr/bin/env python3

from signal import pause

import motepi_patterns as mqtt_handler
import mqtt_config
import mqtt_messages

mqtthandle = mqtt_messages.Messages(mqtt_config)

handlerclass = mqtt_handler.MotePiPatterns(mqtthandle, "MoteControl")
handlerclass.start()

#mqtthandle.setqueuepayload("MoteControl", "BilgeTank", "{}")
pause()
