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
import RPi.GPIO  as gpio
import time

global RUNF, frame

RUNF = {}
frame = 0
pin_led_status = 40 #gpio 21

ch_1 = 1497
ch_2 = 1497
ch_3 = 1497
ch_4 = 1497
yaw = 0
bat = 0
g_speed = 0

offset = 1000


def scale_yaw(value):
    global offset
    if value < 0:
        value = 360 + value
    return value + offset

def conncect_drone():
    global ch_1, ch_2, ch_3, ch_4
    
    if ch_1 == 0:
        ch_1 = 1497
    if ch_2 == 0:
        ch_2 = 1497
    if ch_3 == 0:
        ch_3 = 1497
    if ch_4 == 0:
        ch_4 = 1497
    
    data = np.array( [ch_1, ch_2, ch_3, ch_4, scale_yaw(yaw), g_speed + offset, bat + offset] )
    return ', '.join(str(x) for x in data)

def video_frames_gen():
    global RUNF, frame
    vid = cv2.VideoCapture(0)    
    vid.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    vid.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    while(vid.isOpened()):
        _,frame = vid.read()
        
hilo2 = threading.Thread(target=video_frames_gen).start()   

def send_video_udp(server_socket, client_addr, client_msg):
    global RUNF, frame
    
    if client_msg:
        while True:
            encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
            message = base64.b64encode(buffer)
            server_socket.sendto(message,client_addr)
            if str(client_addr) in RUNF:
                if RUNF[str(client_addr)]:
                    break
    RUNF[str(client_addr)] = False
            
    
def server_udp():
    global RUNF
    subprocess.run(['sudo','fuser','-k','9999/tcp'])
    
    BUFF_SIZE = 65536
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    #server_socket.settimeout(0.2)
    host_name = socket.gethostname()
    host_ip = '192.168.0.200'#  socket.gethostbyname(host_name)
    port = 9999
    socket_address = (host_ip,port)
    server_socket.bind(socket_address)
    print('CAM: Listening at:',socket_address)
    while True:
        try:
            client_msg,addr = server_socket.recvfrom(BUFF_SIZE)
        except:
            client_msg = False
        if client_msg == b'bye':
            RUNF[str(addr)] = True
        if client_msg == b'Hello':
            print('CAM: GOT connection from ',addr, client_msg)
            thread = threading.Thread(target=send_video_udp, args=(server_socket, addr, client_msg)).start()
            print("TOTAL CLIENTS ",threading.activeCount()-2, end='\r')
        time.sleep(0.1)
    os._exist(1)
        
def socket_():
    
    subprocess.run(['sudo','fuser','-k','10000/tcp'])
    connection_string = '/dev/ttyS0' 
    baud_rate = 57600
    #- Connect the UAV
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
    print('Telemetry: vehicle is connected.')
    #-- Read information from the autopilot:
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server_address = ('192.168.0.200', 10000)
    print('Telemetry: starting up on {} port {}'.format(*server_address))
    sock.bind(server_address)
    # Listen for incoming connections
    sock.listen(1)
    i = 1
    while True:
        gpio.setmode(gpio.BOARD)
        gpio.setup(pin_led_status, gpio.OUT)
        gpio.output(pin_led_status, False)
        gpio.output(pin_led_status, True)
        # Wait for a connection
        print('Telemetry: waiting for a connection')
        connection, client_address = sock.accept()
        try:
            print('Telemetry: connection from', client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = conncect_drone()#
                connection.sendall(data.encode('utf-8'))
                time.sleep(0.2)
                
        except:
            # Clean up the connection
            print('Telemetry: closing socket com')
            gpio.cleanup()
            connection.close()
        
if __name__ == '__main__':
    hilo1 = threading.Thread(target=socket_).start()
    hilo2 = threading.Thread(target=server_udp).start()
    


