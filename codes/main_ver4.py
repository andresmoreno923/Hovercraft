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

    #- wait_ready flag hold the program untill all the parameters are been read (=, not .)
    print('vehicle is connected.')
    
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
                data = conncect_drone()#
                connection.sendall(data.encode('utf-8'))
                time.sleep(0.2)
                
        finally:
            # Clean up the connection
            print('closing socket com')
            connection.close()
        

#capture = cv2.VideoCapture('http://192.168.0.12:8000/stream.mjpg')
hilo1 = threading.Thread(target=cam)
hilo2 = threading.Thread(target=socket_)
hilo1.daemon = True
hilo1.start()
hilo2.start()
