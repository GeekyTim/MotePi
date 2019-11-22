# MotePi Configuration
# 2019-10-27

mqttconfig = {"broker": {"host": "WDDrivePi.localdomain",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/pi/MotePi/mqtt-ca.crt"},
              "local": {"deviceid": "MotePi",
                        "username": "MotePi",
                        "password": "MotePi",
                        "device": "MotePi",
                        "version": 1},
              "queues": {"mpqueue": {"name": "MotePi/command",
                                     "qos": 1},
                         "queue2": {"name": "weather/now",
                                    "qos": 1},
                         }
              }
