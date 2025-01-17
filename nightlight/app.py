import time
from grove.grove_light_sensor_v1_2 import GroveLightSensor
from grove.grove_led import GroveLed
import paho.mqtt.client as mqtt
import json


light_sensor = GroveLightSensor(0)
led = GroveLed(5)
id = 'j&npi'
client_name = id + 'nightlight_client'
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'

mqtt_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_name)
mqtt_client.connect('test.mosquitto.org')

mqtt_client.loop_start()
print("MQTT connected!")
led.on()

def handle_command(client, userdata, message):
    payload = json.loads(message.payload.decode())
    print("Message Received: ", payload)
    if payload['led_on']:
        led.on()
    else:
        led.off()

mqtt_client.subscribe(server_command_topic)
mqtt_client.on_message = handle_command


while True:
    light = light_sensor.light
    telemetry = json.dumps({'light' : light})

    print("Sending telemetry", telemetry)

    mqtt_client.publish(client_telemetry_topic, telemetry)

    if light < 300:
        led.on()
    else:
        led.off()
    time.sleep(5)