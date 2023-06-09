
import uuid
import socket
import cv2
import func_num2
import img_overlay
import numpy as np
from flask import Flask, render_template, Response, jsonify, request

app = Flask(__name__)

R = 297.5
top = 0
left = 12

camara = cv2.VideoCapture(0)

hostname = socket.gethostname()

# Una función generadora para stremear la cámara
# https://flask.palletsprojects.com/en/1.1.x/patterns/streaming/


def generador_frames():
    
    overlay = img_overlay.ImageOverlay()
    
    while True:
        print('hola')
        ok, frame = camara.read()
        frame = func_num2.met_lat_long(frame,R,top, left)
        img  = func_num2.filter_(np.uint8(frame),3)
        img = func_num2.resize_frame(img, 800, 600)
        img = overlay.add_transparent_image(img, txt='4.0', cl=1)
        img = overlay.add_transparent_image(img, txt='3.2', cl=0)
        img = overlay.draw_yaw(img, '110')
        img = overlay.draw_rectangle(img, '1497')

        _, bufer = cv2.imencode(".jpg", img)
        imagen = bufer.tobytes()
        yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + imagen + b"\r\n"
            
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    

@app.route('/shutdown', methods=["GET"])
def shutdown():
    return shutdown_server()


# Cuando visiten la ruta
@app.route("/streaming_camara")
def streaming_camara():
    return Response(generador_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Cuando visiten /, servimos el index.html
@app.route('/')
def index():
    return render_template("index.html")


if __name__ == "__main__":
    ip_address = socket.gethostbyname(hostname)
    
    print("Mi dirección IP es:", ip_address)

    app.run(debug=True, host="0.0.0.0")
