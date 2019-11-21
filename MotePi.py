#!/usr/bin/env python3

import motepi_patterns as mqtt_handler
import mqtt_config_MotePi as mqtt_config
import mqtt_messages
import queue

# -----------------------------------------------------------------------------------------------------------------------
# Initialise the MQTT Handler class
handlerqueue = queue.Queue()

handlerclass = mqtt_handler.MQTTHandler(handlerqueue, 1.0/60)
handlerclass.start()

mqtthandle = mqtt_messages.Messages(mqtt_config, handlerclass)

# -----------------------------------------------------------------------------------------------------------------------

mqtthandle.loop_forever()
