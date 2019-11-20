#!/usr/bin/env python3

import threading

import motepi_patterns as mqtt_handler
import mqtt_config_MotePi as mqtt_config
import mqtt_messages

# -----------------------------------------------------------------------------------------------------------------------
# Initialise the MQTT Handler class

handlerclass = mqtt_handler.MQTTHandler()

handlerthread = threading.Thread(target=handlerclass.runmotepi(), args=())
handlerthread.daemon = True
handlerthread.start()
mqtthandle = mqtt_messages.Messages(mqtt_config, handlerthread)

# -----------------------------------------------------------------------------------------------------------------------

mqtthandle.loop_forever()
