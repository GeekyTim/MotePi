# MotePi Configuration
# 2019-10-27

mqttconfig = {"broker": {"host": "WDDrivePi.localdomain",
                         "port": 8883,
                         "keepalive": 60,
                         "transport": "tcp",
                         "tlsversion": 2,
                         "certfile": "/home/pi/mqtt-ca.crt"},
              "local": {"deviceid": "MotePi",
                        "username": "MotePi",
                        "password": "MotePi",
                        "device": "MotePi",
                        "version": 1},
              "queues": {"MoteControl": {"name": "MotePi/command",
                                         "qos": 2}

                         }
              }
