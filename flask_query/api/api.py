import flask
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
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]

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

    
    print(s,d, t)
    try:
        number_of_queries = queries
        mqttc = MyMQTTClass()
        mqttc.connect()
        mqttc.open()
        print("Query sent: {}".format(datetime.now().strftime("%d %b %Y %H:%M:%S.%f")))
        payload = {'x': x, 'y': y, 'number_of_queries': 1, 's': s, 'd': d, 't': t}
        print(payload)
        
        data = json.dumps(payload)
        mqttc.send(GLOBAL_VARS.SIMULATED_SINGLE_QUERY_TO_BROKER, data)
        mqttc.close()
    except ValueError:
        print("Enter an integer for number of queries.")

@app.route('/form_to_json', methods=['GET'])
def refresh():
    s = request.values.get('s')
    d = request.values.get('d')
    t = request.values.get('t')

    send_single_query(int(s), int(d), int(t))
    return "{}, {}, {}".format(s, d, t)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


# A route to return all of the available entries in our catalog.
@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    return jsonify(books)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000) #run app in debug mode on port 5000