# MotePi Configuration
# 2019-10-27

mqttconfig = {"broker": {"host": "mqtt.localdomain",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/pi/MotePi/mqtt-ca.crt"},
              "local": {"deviceid": "MotePi",
                        "username": "user",
                        "password": "pass",
                        "device": "MotePi",
                        "version": 1},
              "queues": {"mpqueue": {"name": "MotePi/command",
                                     "qos": 1}
                         }
              }
