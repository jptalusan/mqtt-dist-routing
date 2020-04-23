"""

A small Test application to show how to use Flask-MQTT.

"""

import eventlet
import json
from flask import Flask, render_template, after_this_request
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask import request, jsonify
import json
import os
import pickle
import sys
import random
from datetime import datetime

sys.path.append('../..')
from common.src import header as generator
from common.src.mqtt_utils import MyMQTTClass
from common.src.basic_utils import time_print
from common.conf import GLOBAL_VARS

eventlet.monkey_patch()

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['MQTT_BROKER_URL'] = '163.221.129.155'
app.config['MQTT_BROKER_PORT'] = 1883
app.config['MQTT_USERNAME'] = ''
app.config['MQTT_PASSWORD'] = ''
app.config['MQTT_KEEPALIVE'] = 5
app.config['MQTT_TLS_ENABLED'] = False

# Parameters for SSL enabled
# app.config['MQTT_BROKER_PORT'] = 8883
# app.config['MQTT_TLS_ENABLED'] = True
# app.config['MQTT_TLS_INSECURE'] = True
# app.config['MQTT_TLS_CA_CERTS'] = 'ca.crt'

mqtt = Mqtt(app)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('publish')
def handle_publish(json_str):
    data = json.loads(json_str)
    print("publishing {} on {}.".format(data['message'], data['topic']))
    mqtt.publish(data['topic'], data['message'])


@socketio.on('subscribe')
def handle_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])


@socketio.on('unsubscribe_all')
def handle_unsubscribe_all():
    mqtt.unsubscribe_all()


@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    socketio.emit('mqtt_message', data=data)
    print("mqtt.on_message()")
    mqtt.publish("middleware/route-response", b"TAE")
    


@mqtt.on_log()
def handle_logging(client, userdata, level, buf):
    print(level, buf)

@mqtt.on_connect()
def handle_connect(client, userdata, flags, rc):
    mqtt.subscribe('middleware/api-response')

@app.route('/form_to_json', methods=['GET'])
def refresh():
    s = request.values.get('s')
    d = request.values.get('d')
    t = request.values.get('t')

    res = send_single_query(int(s), int(d), int(t))
    print(s,d,t)

    return "{}, {}, {}".format(s, d, t)


def send_single_query(s, d, t):
    x, y = 5, 5
    queries = 1
    if not os.path.exists(os.path.join(os.getcwd(), 'data')):
        raise OSError("Must first download data, see README.md")
    data_dir = os.path.join(os.getcwd(), 'data')

    file_path = os.path.join(data_dir, '{}-{}-G.pkl'.format(x, y))
    with open(file_path, 'rb') as handle:
        nx_g = pickle.load(handle)

    if not s:
        s = random.choice(list(nx_g.nodes))
    if not d:
        d = random.choice(list(nx_g.nodes))
    if not t:
        t = random.randint(0,24)

    # print(s,d, t)
    try:
        number_of_queries = queries
        print("Query sent: {}".format(datetime.now().strftime("%d %b %Y %H:%M:%S.%f")))
        payload = {'x': x, 'y': y, 'number_of_queries': 1, 's': s, 'd': d, 't': t}
        print(payload)
        
        data = json.dumps(payload)
        # mqttc.send(GLOBAL_VARS.SIMULATED_SINGLE_QUERY_TO_BROKER, data)
        print(data)
        mqtt.publish(GLOBAL_VARS.SIMULATED_SINGLE_QUERY_TO_BROKER, data)
    except ValueError:
        print("Enter an integer for number of queries.")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, use_reloader=False, debug=True)
    