# MotePi Configuration
# 2019-10-27

# MQTT Server Details
mqtt_BrokerIP = "mqtt.localdomain"
mqtt_BrokerPort = 8883
mqtt_BrokerKeepalive = 60

# Local Device Details
mqtt_localDeviceID = "device"
mqtt_localUsername = "user"
mqtt_localPassword = "passworx"
mqtt_qos = 1

# LED Controller Queues
mqtt_listenqueue = "MotePi/command"

# Certificate file
mqtt_cert = "/home/pi/MotePi/mqtt-ca.crt"

mqtt_expecteddevice = "MotePi"
mqtt_expectedversion = 1
