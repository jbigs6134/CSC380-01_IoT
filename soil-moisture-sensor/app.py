import time
from grove.adc import ADC
from grove.grove_relay import GroveRelay
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse
import json
from os import path
import csv
from datetime import datetime
import threading
from azure.iot.device import IoTHubDeviceClient, Message, MethodResponse

#hub name is soil-moisture-sensor-j because it didn't put
#j&npi at the end of command line
connection_string = "HostName=soil-moisture-sensor-j.azure-devices.net;DeviceId=soil-moisture-sensor;SharedAccessKey=IYQFlXl3AzS2s7BmN4h11ISqP8KA97tNDWUsj6SfY30="

device_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
print('Connecting')
device_client.connect()
print('Connected')

id = 'j&npi'
client_name = id + 'soilmoisturesensor_server'
client_telemetry_topic = id + '/telemetry'
server_command_topic = id + '/commands'

adc = ADC()
relay = GroveRelay(5)

water_time = 5
wait_time = 20

relay_in_progress = False
relay_lock = threading.Lock()

def send_relay_command(client, state):

    command = { 'relay_on' : state }

    print("Sending message:", command)

    client.publish(server_command_topic, json.dumps(command))

def control_relay(client, state):

    global relay_in_progress

    with relay_lock:

        relay_in_progress = True

    send_relay_command(client, state)
    time.sleep(water_time)

    send_relay_command(client, False)
    time.sleep(wait_time)

    with relay_lock:

        relay_in_progress = False

def handle_method_request(request):
    
    print("Direct method received - ", request.name)
    
    if request.name == "relay_on":
        relay.on()
    elif request.name == "relay_off":
        relay.off() 

    method_response = MethodResponse.create_from_method_request(request, 200)
    device_client.send_method_response(method_response)

device_client.on_method_request_received = handle_method_request

while True:

    soil_moisture = adc.read(0)
    telemetry = json.dumps({'Soil Moisture' : soil_moisture})

    print("Sending telemetry: ", telemetry)

    if soil_moisture < 450:

        print("Soil moisture is too low, turning relay on.")
        relay.on() 
        time.sleep(water_time)  

        print("Turning relay off.")
        relay.off() 
        time.sleep(wait_time) 
    else:

        print("Soil moisture is sufficient, turning relay off.")
        relay.off()  

    message = Message(json.dumps({ 'soil_moisture': soil_moisture }))
    device_client.send_message(message)
    
    time.sleep(10)