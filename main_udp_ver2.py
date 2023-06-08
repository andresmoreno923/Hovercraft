
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 08:11:33 2023

@author: andre
"""

import threading
import time
import cv2
import socket
import numpy as np
import base64
import keyboard
import func_num2 

# variable global para almacenar la informacion de telemetria
# ch_1, ch_2, ch_3, ch4, yaw, g_speed, bat
# ch_1 = steearing
# ch_2 = throttle

# ch_3 = y_axis
# ch_4 = x_axis

data_s = None 

fuente = cv2.FONT_HERSHEY_SIMPLEX
color_1 = (0, 0, 255)  # rojo
color_2 = (0, 165, 255)  # naranja
color_3 = (56, 255, 25)  # verde
icon_battery = cv2.imread('battery-icon.png',cv2.IMREAD_UNCHANGED) 

n_cells = 1 #number of battery cells
max_bat_lvl = 4.2  #maximum battery voltage
min_bat_lvl = 3.6  #minimum battery voltage
diff_batt = max_bat_lvl - min_bat_lvl
low_lvl_bat = 0.8 # 20% battery capacity
mod_lvl_bat = 0.25# 75% battery capacity

icon_hvc = cv2.imread('hovercraft_icon.png',cv2.IMREAD_UNCHANGED) 

packet_size = 40
offset = 1000
# alto 1061 1062
# medio 1496
#bajo 1923

def escalar_joystick(valor):
    max_orig = 1062
    min_orig = 1923
    max_escala = 100
    min_escala = -100
    escala = (max_escala - min_escala) / (max_orig - min_orig)
    valor_escala = (valor - min_orig) * escala + min_escala
    return int(valor_escala)


def draw_rectangle(img, data):
    data_j = -1*escalar_joystick(float(data))
    img_h, img_w, _ = img.shape
    pt1 = (img_w-40, int(img_h/2 -100))   # Esquina superior izquierda x - y
    pt2 = (img_w-10, int(img_h/2 +100))   # Esquina inferior derecha
    img = cv2.rectangle(img, pt1, pt2, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
    cv2.putText(img, '__', ( img_w-40,int(img_h/2) + data_j), fuente, 1, color_3 , 1)
    cv2.putText(img, str(-1*data_j), ( img_w-60,int(img_h/2) + data_j), fuente, 0.5, color_3 , 1)
    return img

def draw_yaw(img, data):
    data = float(data) - offset
    n = 20
    img_h, img_w, _ = img.shape
    idx = int(img_w/2)
    indx_ = np.linspace(data-30,data+30,61)
    indx__ = np.linspace(-30,30,61)
    i = 0
    for indx in indx_:
        if not(indx%5):
            #print(idx + n*i,i)
            cv2.putText(img, '|', ( int(idx + n*indx__[i])  ,20), fuente, 0.5, color_3 , 1)
            cv2.putText(img, str(indx), ( int(idx +  n*indx__[i]) ,40), fuente, 0.4, color_3 , 1)
        i = i + 1
    return img

def change_color(img, color):
    alpha_channel = img[:,:,3]
    color_channels = img[:,:,:3]
    
    green_mask = np.logical_and(color_channels[:,:,1] > 0, color_channels[:,:,0] > 0, color_channels[:,:,2] > 0)
    
    if (color == color_1):
        color_channels[green_mask, 0] = 0 
        color_channels[green_mask, 1] = 0 
        color_channels[green_mask, 2] = 255   
    elif (color == color_2):
        color_channels[green_mask, 0] = 0 
        color_channels[green_mask, 1] = 165 
        color_channels[green_mask, 2] = 255   
    elif (color == color_3):
        color_channels[green_mask, 0] = 56 
        color_channels[green_mask, 1] = 255 
        color_channels[green_mask, 2] = 25   
        
    return cv2.merge((color_channels, alpha_channel))

def colour_bat(txt):
    
    if (float(txt) <= n_cells*( max_bat_lvl - low_lvl_bat*diff_batt  ) ):
        color_txt = color_1
    elif ( float(txt) <= n_cells*( max_bat_lvl - mod_lvl_bat*diff_batt  ) ):
        color_txt = color_2 
    elif ( float(txt) >  n_cells*( max_bat_lvl - mod_lvl_bat*diff_batt  ) ): #more than 80% of the maximum battery
        color_txt = color_3
    return color_txt 

def add_transparent_image(bg, fg, x_offset=0, y_offset=0,txt = '0',txt_1 = 'm/s', cl = 1 ):
    txt = np.round(float(txt) - offset,2)
    bg_h, bg_w, bg_channels = bg.shape
    fg_h, fg_w, fg_channels = fg.shape
    
    bg_section = bg[x_offset:x_offset+fg_h,y_offset:y_offset+fg_w,:]
    
    
    if cl:
        color_txt = colour_bat(txt)
        fg= change_color(fg, color_txt) 
    else:
        color_txt = color_3
    
    # separate alpha and color channels from the foreground image
    fg_colors = fg[:, :, :3]
    alpha_channel = fg[:, :, 3] / 255  # 0-255 => 0.0-1.0
    
    # construct an alpha_mask that matches the image shape
    alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

    # combine the background with the overlay image weighted by alpha
    try:
        composite = bg_section * (1 - alpha_mask) + fg_colors * alpha_mask
    except ValueError:
        return
    # overwrite the section of the background image that has been updated
    bg[x_offset:x_offset+fg_h,y_offset:y_offset+fg_w,:] = composite
    
    cv2.putText(bg, str(txt)+str(txt_1), (y_offset+50,x_offset+30) , fuente, 0.7, color_txt , 1)
    return bg

def sock_init_():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.0.9', 10001)
    sock.bind(server_address)
    sock.listen(1)
    while True:
        # Wait for a connection
        print('waiting for a Rover')
        connection, client_address = sock.accept()
        try:
            while True:
                data = connection.recv(1024).decode()
                print('Rover msg received ')
                if data:
                    break
        finally:
            # Clean up the connection
            print('close socket - initialize system')
            connection.close()
            break

def cam():
    global data_s # indicar que se está utilizando la variable global
    BUFF_SIZE = 65536
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
    host_ip = '192.168.0.200'
    port = 9999
    print('connecting CAM')
    
    message = b'Hello'
    client_socket.sendto(message,(host_ip,port))
    
    print('connect CAM')
    R = 297.5
    top = 0
    left = 12
    while True:
        packet,_ = client_socket.recvfrom(BUFF_SIZE)
        data = base64.b64decode(packet,' /')
        npdata = np.fromstring(data,dtype=np.uint8)
        frame = cv2.imdecode(npdata,1)
        
        img = func_num2.met_lat_long(frame,R,top, left)
        img2  = func_num2.filter_(np.uint8(img),3)
        img2 = func_num2.resize_frame(img2, 800, 600)
        
        # throttle g_speed attitude bat
        
        if (data_s is not None):
            img2 = add_transparent_image(img2, icon_battery, 410, 20,data_s[6],'V') #battery
            img2 = add_transparent_image(img2, icon_hvc, 410, 450, data_s[5],'m/s',cl=0) #g_spped
            img2 = draw_yaw(img2, data_s[4])
            img2 = draw_rectangle(img2, data_s[1])
        
        cv2.imshow('webCam',img2)
        if (cv2.waitKey(1) == ord('s')):
            print('closing socket CAM')
            cv2.destroyAllWindows()
            message = b'bye'
            client_socket.sendto(message,(host_ip,port))
            client_socket.close()
            break

def socket_():
    global data_s  # indicar que se está utilizando la variable global
    # Create a TCP/IP socket
    #sock_init_()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        # Connect the socket to the port where the server is listening
        server_address = ('192.168.0.200', 10000)
        print('telemetry: connecting to {} port {}'.format(*server_address))
        sock.connect(server_address)
        print('telemetry: connect {} port {}'.format(*server_address))
        try:
            while True:
                packet = sock.recv(packet_size).decode()
                ndata = packet.split(',')
                if packet:
                    print(packet)
                    if len(packet) == packet_size:
                        data_s = ndata
                if keyboard.is_pressed('s'):
                    print('telemetry: closing socket1')
                    sock.close()
                    break
        except:
            print('telemetry: closing socket2')
        sock.close()


hilo1 = threading.Thread(target=cam)
hilo2 = threading.Thread(target=socket_)
hilo2.daemon = True  # configurar hilo 2 como daemon

hilo1.start()
hilo2.start()
