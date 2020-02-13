import paho.mqtt.client as mqtt

client = mqtt.Client("rsu-0001")
client.connect("localhost")
client.publish("test/topic","FROM container")
