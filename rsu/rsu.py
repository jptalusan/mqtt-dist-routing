import paho.mqtt.client as mqtt
import time
import json
import threading

print(time.time())
print("HELLO")

# http://www.steves-internet-guide.com/mqtt-clean-sessions-example/

import os
hostname = "google.com"
response = os.system("ping -c 1 " + hostname)
if response == 0:
    print("Host is up")

mqtt.Client.connected_flag = False
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))
    
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed: ", str(mid))

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Connected OK")
        client.subscribe("test/topic", qos=1)
        # client.subscribe("#")
    else:
        print("Bad connection RC = ", rc)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        client.loop_stop()
        # client.loop_start()

def mqtt_thread():    
    client = mqtt.Client(client_id="rsu-0001", clean_session=True)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    # client.connect("test.mosquitto.org", port=1883, keepalive=60)
    client.connect("mqtt", port=1883, keepalive=60)

    client.loop_forever()

if __name__ == "__main__":
    mqtt_t = threading.Thread(target=mqtt_thread, args=())
    mqtt_t.start()

    # client = mqtt.Client()

    # client.on_connect = on_connect
    # client.on_disconnect = on_disconnect
    # client.on_subscribe = on_subscribe
    # client.on_message = on_message

    # client.connect("mqtt", 1883, 60)

    # client.loop_forever()