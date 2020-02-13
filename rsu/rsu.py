import paho.mqtt.client as mqtt
import time
import json

print(time.time())
print("HELLO")

mqtt.Client.connected_flag = False
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, message):
    print("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))
    
def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to: ", userdata)
    print(client, userdata, mid, granted_qos)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Connected OK")
        client.subscribe("test/topic")
        client.subscribe("test/hello", qos=1)
    else:
        print("Bad connection RC = ", rc)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")

mqttc.on_disconnect = on_disconnect
client = mqtt.Client("rsu-0001")

client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_subscribe = on_subscribe
client.on_message = on_message

client.loop_start()

client.connect("mqtt", port=1883)
while not client.connected_flag:
    print("in wait loop")
    time.sleep(0.5)

client.publish("test/topic","FROM container2222", qos=1)

client.loop_forever()