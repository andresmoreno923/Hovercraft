from dronekit import connect
import sys
import numpy as np
import time
import subprocess
import keyboard
import pickle
import RPi.GPIO as gpio

ch_1 = 1496
ch_2 = 1496
ch_3 = 1496
ch_4 = 1496
yaw = 0
bat = 0
g_speed = 0
offset = 1000
pin_led_status = 40 #gpio 21

def scale_yaw(value):
    if value < 0:
        value = 360 + value
    return value
    
def conncect_drone():
    global ch_1
    global ch_2
    global ch_3
    global ch_4
    global ch_6
    global yaw
    global g_speed
    global bat
    return np.array( [ch_1, ch_2, ch_3, ch_4, scale_yaw(yaw), g_speed, bat, ch_6] )
    #return ', '.join(str(x) for x in data)

subprocess.run(['sudo','fuser','-k','10000/tcp'])
connection_string = '/dev/ttyS0' 
baud_rate = 57600

gpio.setmode(gpio.BOARD)
gpio.setup(pin_led_status, gpio.OUT)
gpio.output(pin_led_status, False)
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
    global ch_6
    ch_1 = message.chan1_raw
    ch_2 = message.chan2_raw
    ch_3 = message.chan3_raw
    ch_4 = message.chan4_raw
    ch_6 = message.chan6_raw

time.sleep(2)

#- wait_ready flag hold the program untill all the parameters are been read (=, not .)
print('vehicle is connected.')
#-- Read information from the autopilot:
#- Version and attributes
vehicle.wait_ready('autopilot_version')
print('Autopilot version: %s'%vehicle.version)

gpio.output(pin_led_status, True)

while True:
    # Wait for a connection
    data = conncect_drone()
    try:
        with open('vector.pickle','wb') as file:
            pickle.dump(data, file)
    except:
        pass
    time.sleep(0.1)
    

    
    

            
   