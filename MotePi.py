#!/usr/bin/env python3

import motepi_patterns as mqtt_handler
import mqtt_config_MotePi as mqtt_config
import mqtt_messages

# -----------------------------------------------------------------------------------------------------------------------
# Initialise the MQTT Handler class

handlerclass = mqtt_handler.MQTTHandler()
handlerclass.start()

mqtthandle = mqtt_messages.Messages(mqtt_config, handlerclass)

# -----------------------------------------------------------------------------------------------------------------------

mqtthandle.loop_forever()
