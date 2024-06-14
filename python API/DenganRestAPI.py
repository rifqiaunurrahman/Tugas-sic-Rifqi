#!/usr/bin/env python
# coding: utf-8

from flask import Flask, request, jsonify
import paho.mqtt.client as mqtt
import threading
import json

app = Flask(__name__)

# Contoh data dalam bentuk list
data = []

# MQTT settings
MQTT_BROKER = "6ed1c50940ce4ca6bc80a5d95bef5193.s1.eu.hivemq.cloud"
MQTT_PORT = 8883
MQTT_TOPIC_TEMPERATURE = "dht22/suhu"
MQTT_TOPIC_HUMIDITY = "dht22/kelembapan"
MQTT_USERNAME = "Gacorr48"
MQTT_PASSWORD = "8989,Rifzee"

# MQTT client
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe([(MQTT_TOPIC_TEMPERATURE, 0), (MQTT_TOPIC_HUMIDITY, 0)])

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode('utf-8')
    print(f"Received message '{payload}' on topic '{topic}'")

    # Process message and update data
    if topic == MQTT_TOPIC_TEMPERATURE:
        update_data('suhu', str(payload))
    elif topic == MQTT_TOPIC_HUMIDITY:
        update_data('kelembapan', str(payload))

def update_data(key, value):
    if not data:
        new_id = 1
        new_data = {'id': new_id, 'suhu': None, 'kelembapan': None}
        data.append(new_data)
    
    latest_data = data[-1]
    latest_data[key] = value

    # Add a new entry if both temperature and humidity are updated
    if latest_data['suhu'] is not None and latest_data['kelembapan'] is not None:
        new_id = latest_data['id'] + 1
        new_data = {'id': new_id, 'suhu': None, 'kelembapan': None}
        data.append(new_data)

# Setup MQTT client
mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.tls_set()  # Enable TLS for secure connection

def start_mqtt():
    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.loop_forever()

# Start MQTT client in a separate thread
mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.start()

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(data)

@app.route('/api/data/<int:id>', methods=['GET'])
def get_data_by_id(id):
    result = next((item for item in data if item["id"] == id), None)
    if result:
        return jsonify(result)
    else:
        return jsonify({'message': 'Data not found'}), 404

@app.route('/api/data', methods=['POST'])
def add_data():
    req_data = request.get_json()
    if not req_data or 'suhu' not in req_data or 'kelembapan' not in req_data:
        return jsonify({'message': 'Invalid request'}), 400

    new_id = len(data) + 1
    new_data = {
        'id': new_id,
        'suhu': req_data['suhu'],
        'suhu': req_data['kelembapan']
    }
    data.append(new_data)
    return jsonify({'message': 'Data added successfully', 'data': new_data}), 201

if __name__ == '__main__':
    app.run(debug=True, port=1234)
