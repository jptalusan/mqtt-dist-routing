import paho.mqtt.client as mqtt
import threading
import time

# https://github.com/dm8tbr/org.eclipse.paho.mqtt.python/blob/master/examples/sub-class.py
class MyMQTTClass:

    mqtt.Client.connected_flag = False

    def __init__(self, client_id=None, host="localhost", port=1883, keep_alive=60, clean_session=True):
        self._mqttc = mqtt.Client(client_id=client_id, clean_session=clean_session)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_disconnect = self.mqtt_on_disconnect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe

        self._client_id = client_id
        self._host = host
        self._port = port
        self._keep_alive = keep_alive
        self._sub_thread_flag = False

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        self._mqttc.connected_flag = True
        print("rc: "+str(rc))

    def mqtt_on_disconnect(client, userdata, rc):
        if rc != 0:
            self._mqttc.connected_flag = False
            print("Unexpected disconnection.")
            client.loop_stop()

    def mqtt_on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        if msg.topic == "test/topic2":
            self._mqttc.publish("test/topic", msg.payload, qos=0, retain=False)

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("Sent message: "+str(mid))

    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)

    def connect(self, debug=False):
        try:
            if debug:
                self._mqttc.connect("test.mosquitto.org", 1883, 60)
            else:
                self._mqttc.connect(self._host, 1883, 60)
        except ConnectionRefusedError as e:
            print(e)
            return e

    def open(self):
        if not self._sub_thread_flag:
            self._mqttc.loop_start()

    def send(self, topic, payload):
        # If not yet connected will not send. But if with this, the query code gets stuck
        while not self._mqttc.connected_flag:
            print("in wait loop")
            time.sleep(1)
        self._mqttc.publish(topic, payload, qos=0, retain=False)

    def close(self):
        rc = self._mqttc.loop_stop()
        return rc

    def sub_thread(self, topic_arr):
        self._sub_thread_flag = True
        for topic in topic_arr:
            self._mqttc.subscribe(topic, 0)
        self._mqttc.loop_forever()

    def start_sub_thread(self, topic_arr):
        mqtt_t = threading.Thread(target=self.sub_thread, args=(topic_arr,))
        mqtt_t.start()


# $SYS messages
# '$SYS/broker/version',
# '$SYS/broker/uptime',
# '$SYS/broker/load/messages/received/1min', 
# '$SYS/broker/load/messages/received/5min', 
# '$SYS/broker/load/messages/received/15min', 
# '$SYS/broker/load/messages/sent/1min', 
# '$SYS/broker/load/messages/sent/5min', 
# '$SYS/broker/load/messages/sent/15min', 
# '$SYS/broker/load/publish/sent/1min', 
# '$SYS/broker/load/publish/sent/5min', 
# '$SYS/broker/load/publish/sent/15min', 
# '$SYS/broker/load/bytes/received/1min', 
# '$SYS/broker/load/bytes/received/5min', 
# '$SYS/broker/load/bytes/received/15min', 
# '$SYS/broker/load/bytes/sent/1min', 
# '$SYS/broker/load/bytes/sent/5min', 
# '$SYS/broker/load/bytes/sent/15min', 
# '$SYS/broker/load/sockets/5min', 
# '$SYS/broker/load/sockets/15min', 
# '$SYS/broker/load/connections/5min', 
# '$SYS/broker/load/connections/15min', 
# '$SYS/broker/messages/received', 
# '$SYS/broker/messages/sent', 
# '$SYS/broker/store/messages/bytes', 
# '$SYS/broker/bytes/received', 
# '$SYS/broker/bytes/sent', 