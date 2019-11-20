import json

import paho.mqtt.client as mqtt


class Messages:
    def __init__(self, config, handlerclass):
        self.__device = config.mqtt_expecteddevice
        self.__version = config.mqtt_expectedversion
        self.__template = {"mqttmessage": {
            "device": self.__device,
            "version": self.__version,
            "payload": {}}
        }

        self.__listenqueue = config.mqtt_listenqueue
        self.__qos = config.mqtt_qos
        self.__handlerclass = handlerclass

        mqttclient = self.startmqtt(config)

        mqttclient.loop_forever()

    # -----------------------------------------------------------------------------------------------------------------------
    # MQTT Handling callback Functions
    # The callback for when the client receives a CONNACK response from the server.
    def startmqtt(self, config):
        client = mqtt.Client(client_id=config.mqtt_localDeviceID, clean_session=True, transport="tcp")
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_log = self.on_log
        client.tls_set(config.mqtt_cert, tls_version=2)

        client.username_pw_set(username=config.mqtt_localUsername,
                               password=config.mqtt_localPassword)
        client.connect(config.mqtt_BrokerIP, config.mqtt_BrokerPort,
                       keepalive=config.mqtt_BrokerKeepalive)

        return client

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        client.subscribe(topic=self.__listenqueue, qos=self.__qos)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        print("Got a message")

        payload = self.getpayload(msg)
        if payload != {}:
            self.__handlerclass.handlemqtt(payload)
        else:
            print("Error in Payload")

    def on_publish(self, client, obj, mid):
        pass

    def on_log(self, client, obj, level, string):
        print(string)

    # MQTT message interpreter - used to verify we have the right message format
    def jsontodict(self, jsonmessage):
        try:
            message_json = jsonmessage.payload.decode("utf-8")
            message = json.loads(message_json)
        except:
            print("Error: jsontodict", jsonmessage)
            message = {}

        return message

    def ismqttmessage(self, message):
        return "mqttmessage" in message

    def isrightdevice(self, message):
        response = False
        if "device" in message["mqttmessage"]:
            if message["mqttmessage"]["device"] == self.__device:
                response = True
        return response

    def isrightversion(self, message):
        response = False
        if "version" in message["mqttmessage"]:
            if message["mqttmessage"]["version"] == self.__version:
                response = True
        return response

    def haspayload(self, message):
        response = False
        if "payload" in message["mqttmessage"]:
            payload = self.extractpayload(message)
            if "command" in payload and "params" in payload:
                response = True

        return response

    def extractpayload(self, message):
        return message["mqttmessage"]["payload"]

    def getpayload(self, mqttmessage):
        message = self.jsontodict(mqttmessage)
        print(message)

        payload = {}
        if self.ismqttmessage(message):
            print("ismqttmessage")
            if self.isrightdevice(message):
                print("isrightdevice")
                if self.isrightversion(message):
                    print("isrightversion")
                    if self.haspayload(message):
                        print("haspayload")
                        payload = self.extractpayload(message)

        return payload

    def generatepayload(self, command, paramdict):
        payload = {"command": command,
                   "params": paramdict}
        return payload

    def generatemessage(self, payload):
        messagedict = self.__template
        messagedict["mqttmessage"]["payload"] = payload
        return messagedict

    def generatemessage_json(self, messagedict):
        try:
            message = json_dumps(messagedict)
        except:
            message = ""
        return message
