from dronekit import connect
import socket
import sys
import numpy as np
import time

def conncect_drone(vehicle):
    attitude = np.rad2deg([vehicle.attitude.roll,vehicle.attitude.pitch,vehicle.attitude.yaw]) 
    g_speed = vehicle.groundspeed #ground speed
    lat = vehicle.location.global_frame.lat
    long = vehicle.location.global_frame.lon
    alt = vehicle.location.global_frame.alt
    # Get all original channel values (before override)
    y_axis = (vehicle.channels['3'] - 1066-867/2)/(-867/2)
    x_axis = (vehicle.channels['4'] - 1066-867/2)/(867/2)
    z_axis = (vehicle.channels['1'] - 1066-867/2)/(867/2)
    
    data = np.array([x_axis,y_axis,z_axis,g_speed,lat,long,alt])
    return np.concatenate((data, attitude), axis=0)


connection_string = '/dev/ttyS0' 
baud_rate = 57600
#- Connect the UAV
print(">>>> Connecting with the UAV <<<")
vehicle = connect(connection_string, baud= baud_rate, wait_ready=True)
#- wait_ready flag hold the program untill all the parameters are been read (=, not .)
print('vehicle is connected.')
#-- Read information from the autopilot:
#- Version and attributes
vehicle.wait_ready('autopilot_version')
print('Autopilot version: %s'%vehicle.version)


while True:
    #data = data + (1/10)*np.random.uniform(-1, 1, size=7)
    #data = np.array2string(data, precision=2, separator=',',suppress_small=True)
    data = conncect_drone(vehicle)

    print(data)
    #break
    time.sleep(0.1)
