from dronekit import connect
import socket
import sys
import numpy as np
import time
import subprocess

ch_1 = 0
ch_2 = 0
ch_3 = 0
ch_4 = 0
yaw = 0
bat = 0
g_speed = 0
offset = 1000


def scale_yaw(value):
    if value < 0:
        value = 360 + value
    return value + offset
    
def conncect_drone():
    data = np.array( [ch_1, ch_2, ch_3, ch_4, scale_yaw(yaw), g_speed + offset, bat + offset] )
    return ', '.join(str(x) for x in data)

subprocess.run(['sudo','fuser','-k','10000/tcp'])
connection_string = '/dev/ttyS0' 
baud_rate = 57600
#- Connect the UAV
print(">>>> Connecting with the UAV <<<")
vehicle = connect(connection_string, baud= baud_rate, wait_ready=True)

@vehicle.on_message('GROUNDSPEED')
def gspeed_listener(self, name, message):
    global g_speed
    g_speed = np.round(message.g_speed,1)

@vehicle.on_message('BATTERY')
def battery_listener(self, name, message):
    global bat
    bat = np.round(message.bat,2)
    
@vehicle.on_message('ATTITUDE')
def attitude_listener(self, name, message):
    global yaw
    yaw = np.rad2deg(message.yaw).astype(int)

@vehicle.on_message('RC_CHANNELS')
def chin_listener(self, name, message):
    global ch_1
    global ch_2
    global ch_3
    global ch_4
    ch_1 = message.chan1_raw
    ch_2 = message.chan2_raw
    ch_3 = message.chan3_raw
    ch_4 = message.chan4_raw

time.sleep(2)

#- wait_ready flag hold the program untill all the parameters are been read (=, not .)
print('vehicle is connected.')
#-- Read information from the autopilot:
#- Version and attributes
vehicle.wait_ready('autopilot_version')
print('Autopilot version: %s'%vehicle.version)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('192.168.0.200', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            data = conncect_drone()
            connection.sendall(data.encode('utf-8'))
            print(len(data.encode('utf-8')),data)
            time.sleep(0.1)

            
    finally:
        # Clean up the connection
        connection.close()