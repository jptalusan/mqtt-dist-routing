import paho.mqtt.client as mqtt
import time
import random
import string
import json
import threading
from multiprocessing import Pool as ThreadPool

def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

# Q- Does it make sense to have a very long keep alive period?
# A- Personally if I was expecting that a client would have very long periods (>15mins) of total inactivity I would disconnect it, and reconnect when It had data to send.
print(time.time())
print("HELLO")

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
        # client.subscribe("test/topic", qos=1)
        # client.subscribe("test/hello", qos=0)
        # client.subscribe("#")
    else:
        print("Bad connection RC = ", rc)

def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        client.loop_stop()
        # client.loop_start()

def publish_messages(host, number_of_messages, topic="test/topic", clean_session=True):
    client_id = randomString()
    print("Client: ", client_id)

    client = mqtt.Client(client_id=client_id, clean_session=clean_session)
    client.on_connect = on_connect

    try:
        client.connect(host)
    except ConnectionRefusedError as e:
        print(e)
        return

    client.loop_start()
    while not client.connected_flag:
        print("in wait loop")
        time.sleep(1)

    count = number_of_messages
    while count != 0:
        message = "{}:{}".format(client_id, str(count))
        client.publish(topic, message, qos=1, retain=True)
        time.sleep(0.02)
        count -= 1
        print(count)

    client.loop_stop()

# function to be mapped over
def calculateParallel(host, number_of_messages, topic="test/topic", clean_session=True, threads=2):
    pool = ThreadPool(threads)
    # results = pool.map(publish_messages, args=(host, number_of_messages, topic, clean_session,))
    res = pool.apply_async(publish_messages, args=(host, number_of_messages, topic, clean_session,))      # runs in *only* one process
    res2 = pool.apply_async(publish_messages, args=(host, number_of_messages, topic, clean_session,))      # runs in *only* one process
    res3 = pool.apply_async(publish_messages, args=(host, number_of_messages, topic, clean_session,))      # runs in *only* one process
    pool.close()
    pool.join()
    return res

if __name__ == "__main__":
    # mqtt_t = threading.Thread(target=publish_messages, args=("localhost", 500, "test/topic", False,))
    # mqtt_t.start()

    numbers = [1, 2, 3, 4, 5]
    squaredNumbers = calculateParallel("localhost", 500, "test/topic", False, threads=4)
    print("Done")