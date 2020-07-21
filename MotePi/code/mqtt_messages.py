import json

import mqtt_config as config
import paho.mqtt.client as mqtt
from dynamicdictionary import dictionary

''' The expected format of the messages that this code will handle is the following JSON: 
    {"mqttmessage": {
            "device": "thisdevice",
            "version": 1,
            "payload": {
				"command": "acommand",
				"params": {"param1":"value1"}
			}
		}
    }
'''


class Messages:
    def __init__(self, handlerclass):
        self.__device = config.mqttconfig["local"]["device"] # This device
        self.__version = config.mqttconfig["local"]["version"] # The GeekyTim MQTT version
        self.__transport = config.mqttconfig["broker"]["transport"]
        self.__certfile = config.mqttconfig["broker"]["certfile"]
        self.__tlsversion = config.mqttconfig["broker"]["tlsversion"]
        self.__user = config.mqttconfig["local"]["username"]
        self.__password = config.mqttconfig["local"]["password"]
        self.__host = config.mqttconfig["broker"]["host"]
        self.__port = config.mqttconfig["broker"]["port"]
        self.__keepalive = config.mqttconfig["broker"]["keepalive"]

        # A templace when we want to output a message - insert the payload in 'payload'
        self.__output_message_template = {"mqttmessage": {"device": self.__device, "version": self.__version, "payload": {}}}

        # The format of the payload
        self.__payloadtemplate = {"command": "", "params": {}}

        # Queues to listen to
        self.__listenqueues = config.mqttconfig["queues"]
        self.__queuepayloads = self.__makequeuedef(self.__listenqueues)
        self.__handlerclass = handlerclass

        # Start listening to the queue
        client = self.__startmqtt()
        client.loop_start()

    # -----------------------------------------------------------------------------------------------------------------------
    # MQTT Handling callback Functions
    # The callback for when the client receives a CONNACK response from the server.
    def __startmqtt(self):
        """ Start the connection to MQTT - The configuration is in 'config'"""
        client = mqtt.Client(client_id=config.mqttconfig["local"]["deviceid"], clean_session=True,
                             transport=config.mqttconfig["broker"]["transport"])
        client.tls_set(config.mqttconfig["broker"]["certfile"], tls_version=config.mqttconfig["broker"]["tlsversion"])

        client.username_pw_set(username=config.mqttconfig["local"]["username"],
                               password=config.mqttconfig["local"]["password"])

        client.on_connect = self.__on_connect
        client.on_message = self.__on_message
        client.on_log = self.__on_log

        client.connect(host=config.mqttconfig["broker"]["host"], port=config.mqttconfig["broker"]["port"],
                       keepalive=config.mqttconfig["broker"]["keepalive"])

        return client

    def __on_connect(self, client, userdata, flags, rc):
        """ This is run once this server connects with MQTT """
        print("Connected with result code " + str(rc))

        # Subscribing in __on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for queue in self.__listenqueues:
            client.subscribe(topic=self.__listenqueues[queue]["name"], qos=self.__listenqueues[queue]["qos"])

    # The callback for when a PUBLISH message is received from the server.
    def __on_message(self, client, userdata, msg):
        """ When a message is received, ensure that it is the correct format """
        payload = self.__getpayloadcontents(msg)
        if payload != {}:
            topic = msg.topic

            for queue in self.__listenqueues:
                if self.__listenqueues[queue]['name'] == topic:
                    self.__handlerclass.messagehandler(payload['command'], payload['params'])
        else:
            print("Error in Payload")

    def __on_publish(self, client, obj, mid):
        """ What to do when a message is published """
        pass

    def __on_log(self, client, obj, level, string):
        """ When a log is required """
        print(string)

    # MQTT message interpreter - used to verify we have the right message format
    def __jsontodict(self, jsonmessage):
        """ Converts a JSON message to a python dictionary """
        message = ""
        try:
            message_json = jsonmessage.payload.decode("utf-8")
            message = json.loads(message_json)
        except:
            print("Error: __jsontodict", jsonmessage)
            message = {}
        finally:
            return message

    def __ismqttmessage(self, message):
        """ Returns true if 'mqttmessage' is in the message i.e. if it is likely to be using the predefined message
        format """
        return "mqttmessage" in message

    def __isrightdevice(self, message):
        """ Is this message destined for this device? """
        response = False
        if "device" in message["mqttmessage"]:
            if message["mqttmessage"]["device"] == self.__device:
                response = True
        return response

    def __isrightversion(self, message):
        """ Is the message the correct version for this program """
        response = False
        if "version" in message["mqttmessage"]:
            if message["mqttmessage"]["version"] == self.__version:
                response = True
        return response

    def __haspayload(self, message):
        """ Does the message have a 'payload' """
        response = False
        if "payload" in message["mqttmessage"]:
            payload = self.__extractpayload(message)
            if "command" in payload and "params" in payload:
                response = True

        return response

    def __extractpayload(self, message):
        """ Extracts the payload from the message """
        return message["mqttmessage"]["payload"]

    def __getpayloadcontents(self, mqttmessage):
        """ Returns the payload """
        message = self.__jsontodict(mqttmessage)
        payload = {}
        if self.__ismqttmessage(message):
            if self.__isrightdevice(message):
                if self.__isrightversion(message):
                    if self.__haspayload(message):
                        payload = self.__extractpayload(message)

        return payload

    def __getqueuepayload(self, queuename):
        payload = ""
        try:
            payload = self.__queuepayloads[queuename]
        except:
            payload = {}
        finally:
            return payload

    def __setqueuepayload(self, queue, command, params):
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

    def __makequeuedef(self, queuedef):
        localdic = dictionary()
        for queue in queuedef:
            localdic.add(queue, self.__payloadtemplate)

        return localdic
