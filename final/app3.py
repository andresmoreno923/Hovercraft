import threading
from dronekit import connect
import time
import uuid
import cv2
import func_num2
import img_overlay
import img_cropp
import numpy as np
import pickle
from flask import Flask, render_template, Response, jsonify, request
from pathlib import Path
import RPi.GPIO as gpio

ch_1 = 1496
ch_2 = 1496
ch_3 = 1496
ch_4 = 1496
ch_6 = 1496
yaw = 0
bat = 0
g_speed = 0
data = np.array([1497,1497,1497,1497,110,0,0,1497])
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


def drone_tel():
    global data
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

    #while True:
        #data = conncect_drone()
        #time.sleep(0.1)
        

app = Flask(__name__)

R = 297.5
top = 0
left = 12

# Una función generadora para stremear la cámara
# https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/

def generador_frames():
    global data
    camara = cv2.VideoCapture(0)
    overlay = img_overlay.ImageOverlay()
    img_w = 800
    img_h = 600
    cropp = img_cropp.ImageCropped(img_w, img_h)    
    start = time.time()
    while (camara.isOpened()):
        ok, frame = camara.read()
        
        end = time.time()
        if (end - start >=0.1): 
            data = conncect_drone() 
            start = end
            
        frame = func_num2.met_lat_long(frame,R,top, left)
        img  = func_num2.filter_(np.uint8(frame),3)
        img = func_num2.resize_frame(img, img_w, img_h)
        img = cropp.imgcropp(img, data[3], data[2])
        
        sbs = int(50*(cropp.scale(data[7]) + 1))
        
        img1 = np.copy(img[:,0:img.shape[1]-sbs,:]) 
        img2 = np.copy(img[:,sbs:,:])
        
        img1 = overlay.add_overlay(img1, data)
        img2 = overlay.add_overlay(img2, data)
        
        img = cv2.hconcat([img1, img2])
        #img = overlay.add_overlay(img, data)
        
        #img = overlay.add_transparent_image(img, txt=data[6], cl=1)
        #img = overlay.add_transparent_image(img, txt=data[5], cl=0)
        #img = overlay.draw_yaw(img, data[4])
        #img = overlay.draw_rectangle(img, data[1])
        
        _, bufer = cv2.imencode(".jpg", img)
        imagen = bufer.tobytes()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"
            
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
def web():
    #from waitress import serve
    #serve(app, host="0.0.0.0")
    app.run(debug = False, host="0.0.0.0")
    
# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route("/shutdown", methods=["GET"])
def shutdown():
    return shutdown_server()
# Cuando visiten /, servimos el index.html
@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    threading.Thread(target=drone_tel).start()
    threading.Thread(target=web).start()
        
    
