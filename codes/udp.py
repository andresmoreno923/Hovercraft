# This is server code to send video frames over UDP

# This is server code to send svideo frames over UDP
import cv2, socket
import numpy as np
import time
import base64

BUFF_SIZE = 65536
server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF,BUFF_SIZE)
host_name = socket.gethostname()
host_ip = '192.168.0.200'#  socket.gethostbyname(host_name)
print(host_ip)
port = 9999
socket_address = (host_ip,port)
server_socket.bind(socket_address)
print('Listening at:',socket_address)
vid = cv2.VideoCapture(0) #  replace 'rocket.mp4' with 0 for webcam
resolution = [(640, 480),(800,600),(1280, 720),(1920, 1080)]
i = 0
vid.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[i][0])
vid.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[i][1])

while True:
	msg,client_addr = server_socket.recvfrom(BUFF_SIZE)
	print('GOT connection from ',client_addr)
	WIDTH=400
	while(vid.isOpened()):
        
		_,frame = vid.read()
		encoded,buffer = cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
		message = base64.b64encode(buffer)
		server_socket.sendto(message,client_addr)
		
		#cv2.imshow('TRANSMITTING VIDEO',frame)
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			server_socket.close()
			break
