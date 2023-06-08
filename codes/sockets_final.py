from dronekit import connect
import socket
import sys
import numpy as np
import time

def escalar_valor(valor_original, valor_minimo_original, valor_maximo_original, valor_minimo_deseado, valor_maximo_deseado):
    valor_escalado = ((valor_original - valor_minimo_original) / (valor_maximo_original - valor_minimo_original)) * (valor_maximo_deseado - valor_minimo_deseado) + valor_minimo_deseado
    return valor_escalado

def conncect_drone(i,vehicle):
    attitude = np.round(np.rad2deg([vehicle.attitude.roll,vehicle.attitude.pitch,vehicle.attitude.yaw])).astype(int)
    #g_speed = vehicle.groundspeed #ground speed
    
    #lat = vehicle.location.global_frame.lat
    #long = vehicle.location.global_frame.lon
    #alt = vehicle.location.global_frame.alt
    # Get all original channel values (before override)
    y_axis = vehicle.channels['3']
    #x_axis = escalar_valor(vehicle.channels['4'], 1066, 1734, -100, 100)
    x_axis = vehicle.channels['4']
    z_axis = vehicle.channels['1'] 
    
    #data = np.concatenate(([x_axis], attitude), axis=0)
    data = np.array( [x_axis,y_axis,z_axis,i] )
    #return str(x_axis),',',str(y_axis),',',str(z_axis),',',str(i)
    return ', '.join(str(x) for x in data)
    #return np.concatenate((x_axis, attitude), axis=0)


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

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Bind the socket to the port
server_address = ('192.168.0.12', 10000)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)
i = 1
while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from', client_address)

        # Receive the data in small chunks and retransmit it
        while True:
            #data = data + (1/10)*np.random.uniform(-1, 1, size=7)
            #data = np.array2string(data, precision=2, separator=',',suppress_small=True)
            
            data = conncect_drone(i,vehicle)
            print(data)
            connection.sendall(data.encode('utf-8'))
            data = 0
            #np.set_printoptions(suppress=True)
            #print(data)
            #break
            time.sleep(0.1)
            i = i + 1
   
            
    finally:
        # Clean up the connection
        print('closing socket com')
        connection.close()
        