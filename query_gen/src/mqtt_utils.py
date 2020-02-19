import paho.mqtt.client as mqtt
import threading
import time

# https://github.com/dm8tbr/org.eclipse.paho.mqtt.python/blob/master/examples/sub-class.py
class MyMQTTClass:
    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True):
        self._mqttc = mqtt.Client(client_id=client_id, clean_session=clean_session)
        # self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_disconnect = self.mqtt_on_disconnect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        print("rc: "+str(rc))

    def mqtt_on_disconnect(client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")
            client.loop_stop()

    def mqtt_on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        if msg.topic == "test/topic2":
            self._mqttc.publish("test/topic", msg.payload, qos=0, retain=False)

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self):
        self._mqttc.connect("test.mosquitto.org", 1883, 60)
        # self._mqttc.connect("localhost", 1883, 60)
        self._mqttc.subscribe("$SYS/#", 0)
        rc = 0
        while rc == 0:
            rc = self._mqttc.loop()
        return rc

    def connect(self, debug=False):
        if debug:
            self._mqttc.connect("test.mosquitto.org", 1883, 60)
        else:
            self._mqttc.connect("localhost", 1883, 60)
        
    def sub(self):
        # self._mqttc.subscribe("$SYS/#", 0)
        self._mqttc.subscribe("test/topic", 0)
        self._mqttc.loop_forever()
        # rc = 0
        # while rc == 0:
        #     rc = self._mqttc.loop()
        # return rc

    def open(self):
        self._mqttc.loop_start()

    def send(self, payload):
        self._mqttc.publish("test/topic", payload, qos=0, retain=False)

    def close(self):
        rc = self._mqttc.loop_stop()
        return rc

    def sub_thread(self, topic_arr):
        # self._mqttc.subscribe("$SYS/#", 0)
        for topic in topic_arr:
            self._mqttc.subscribe(topic, 0)
        self._mqttc.loop_forever()

    def start_sub_thread(self, topic_arr):
        mqtt_t = threading.Thread(target=self.sub_thread, args=(topic_arr,))
        mqtt_t.start()