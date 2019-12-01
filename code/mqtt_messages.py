import json

import paho.mqtt.client as mqtt
from dynamicdictionary import dictionary


class Messages:
    def __init__(self, config):
        self.__device = config.mqttconfig["local"]["device"]
        self.__version = config.mqttconfig["local"]["version"]
        self.__template = {"mqttmessage": {
            "device": self.__device,
            "version": self.__version,
            "payload": {}
        }
        }
        self.__payloadtemplate = {"command": "",
                                  "params": {}}

        self.__listenqueues = config.mqttconfig["queues"]
        self.__queuepayloads = self.makequeuedef(self.__listenqueues)

        client = self.startmqtt(config)
        client.loop_start()

    # -----------------------------------------------------------------------------------------------------------------------
    # MQTT Handling callback Functions
    # The callback for when the client receives a CONNACK response from the server.
    def startmqtt(self, config):
        client = mqtt.Client(client_id=config.mqttconfig["local"]["deviceid"],
                             clean_session=True, transport=config.mqttconfig["broker"]["transport"])
        client.tls_set(config.mqttconfig["broker"]["certfile"], tls_version=config.mqttconfig["broker"]["tlsversion"])

        client.username_pw_set(username=config.mqttconfig["local"]["username"],
                               password=config.mqttconfig["local"]["password"])

        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_log = self.on_log

        client.connect(host=config.mqttconfig["broker"]["host"], port=config.mqttconfig["broker"]["port"],
                       keepalive=config.mqttconfig["broker"]["keepalive"])

        return client

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for queue in self.__listenqueues:
            client.subscribe(topic=self.__listenqueues[queue]["name"], qos=self.__listenqueues[queue]["qos"])

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, msg):
        payload = self.getpayloadcontents(msg)
        if payload != {}:
            topic = msg.topic
            for queue in self.__listenqueues:
                if self.__listenqueues[queue]['name'] == topic:
                    self.setqueuepayload(queue, payload['command'], payload['params'])
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

    def getpayloadcontents(self, mqttmessage):
        message = self.jsontodict(mqttmessage)
        payload = {}
        if self.ismqttmessage(message):
            if self.isrightdevice(message):
                if self.isrightversion(message):
                    if self.haspayload(message):
                        payload = self.extractpayload(message)

        return payload

    def getqueuepayload(self, queuename):
        try:
            payload = self.__queuepayloads[queuename[0]]
        except:
            payload = {}
        finally:
            return payload

    def setqueuepayload(self, queue, command, params):
        try:
            self.__queuepayloads[queue]['command'] = command
            self.__queuepayloads[queue]['params'] = params
        except:
            self.__queuepayloads['queues'][queue]['command'] = ""
            self.__queuepayloads['queues'][queue]['params'] = {}

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

    def makequeuedef(self, queuedef):
        localdic = dictionary()
        for queue in queuedef:
            localdic.add(queue, self.__payloadtemplate)

        return localdic
