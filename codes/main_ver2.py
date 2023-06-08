from dronekit import connect
import threading
import random
import time
import cv2
import socket
import sys
import numpy as np
import base64
import keyboard
import math
import uuid
import subprocess

def socket_init_():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.0.9', 10001)
    print('connecting to {} port {}'.format(*server_address))
    sock.connect(server_address)
    try:
        message = b'threading socket init.'
        sock.sendall(message)
    finally:
        print('closing socket')
        sock.close()


def conncect_drone(i,vehicle):
    attitude = np.round(np.rad2deg([vehicle.attitude.roll,vehicle.attitude.pitch,vehicle.attitude.yaw])).astype(int)
    g_speed = vehicle.groundspeed #ground speed
    bat = vehicle.battery.voltage
    #lat = vehicle.location.global_frame.lat
    #long = vehicle.location.global_frame.lon
    #alt = vehicle.location.global_frame.alt
    throttle = vehicle.channels['2']
    print(type(throttle))
    #x_axis = escalar_valor(vehicle.channels['4'], 1066, 1734, -100, 100)
    #data = np.concatenate(([x_axis], attitude), axis=0)
    data = np.array( [throttle,g_speed,attitude[2],bat] )

    return ', '.join(str(x) for x in data)



def cam():
    subprocess.run(['sudo','fuser','-k','9999/tcp'])
    
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    host_name = socket.gethostname()
    host_ip = '192.168.0.200'#  socket.gethostbyname(host_name)
    port = 9999
    socket_address = (host_ip,port)
    server_socket.bind(socket_address)
    print('Listening at:',socket_address)
    vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
        print('GOT connection from ',client_addr)
        while(vid.isOpened()):
            _,frame = vid.read()
            encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            message = base64.b64encode(buffer)
            server_socket.sendto(message,client_addr)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                server_socket.close()
                break
    server_socket.close()

def socket_():
    
    subprocess.run(['sudo','fuser','-k','10000/tcp'])
    connection_string = '/dev/ttyS0' 
    baud_rate = 57600
    #- Connect the UAV
    print(">>>> Connecting with the UAV <<<<")
    vehicle = connect(connection_string, baud= baud_rate, wait_ready=True)
    #- wait_ready flag hold the program untill all the parameters are been read (=, not .)
    print('vehicle is connected.')
    socket_init_()
    #-- Read information from the autopilot:
    # Create a TCP/IP socket
    print(">>>> Connecting with the socket 10000 <<<<")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('192.168.0.200', 10000)
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
                data = conncect_drone(i,vehicle)#
                print(data)
                connection.sendall(data.encode('utf-8'))
                time.sleep(0.5)
                
        finally:
            # Clean up the connection
            print('closing socket com')
            connection.close()
        

#capture = cv2.VideoCapture('http://192.168.0.12:8000/stream.mjpg')
hilo1 = threading.Thread(target=cam)
hilo2 = threading.Thread(target=socket_)
hilo1.start()
hilo2.start()
hilo1.join()
hilo2.join()
