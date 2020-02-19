import paho.mqtt.client as mqtt
from pymongo import MongoClient
# pprint library is used to make the output look more pretty
from pprint import pprint
import time

mqtt.Client.connected_flag = False

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True
        print("Connected OK")
    else:
        print("Bad connection RC = ", rc)

mqtt_client = mqtt.Client(client_id="broker", clean_session=True)
mqtt_client.on_connect = on_connect

try:
    mqtt_client.connect("mqtt")
except ConnectionRefusedError as e:
    print(e)

mqtt_client.loop_start()
while not mqtt_client.connected_flag:
    print("in wait loop")
    time.sleep(1)

count = 5
while count != 0:
    message = "{}:{}".format("broker", str(count))
    mqtt_client.publish("test/topic", message, qos=0, retain=False)
    time.sleep(0.02)
    count -= 1
    print(count)

mqtt_client.loop_stop()

mongo_client = MongoClient("mongo")
db=mongo_client.admin
# Issue the serverStatus command and print the results
# serverStatusResult=db.command("serverStatus")
# pprint(serverStatusResult)


t = {'job':"A", 't_id':"0001"}
result = db.tasks.insert_one(t)
print('Created {0} of 0 as {1}'.format(0, result.inserted_id))

task = db.tasks.find_one({'job': "B"})
print(task)

