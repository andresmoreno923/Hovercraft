# -*- coding: utf-8 -*-
"""
Created on Mon Jun  5 16:34:02 2023

@author: andre
"""


import os
import cv2
import func_num2
import numpy as np
import img_overlay

R = 297.5
top = 0
left = 12

capture = cv2.VideoCapture(0)

overlay = img_overlay.ImageOverlay()

while (capture.isOpened()):
    
    ret, frame = capture.read()
    
    
    img = func_num2.met_lat_long(frame,R,top, left)
    img  = func_num2.filter_(np.uint8(img),3)
    img = func_num2.resize_frame(img, 800, 600)
    
    img = overlay.add_transparent_image(img, txt='3.2', cl=0)
    img = overlay.add_transparent_image(img, txt='4.0', cl=1)
    img = overlay.add_transparent_image(img, txt='-70.1', cl=2)
    img = overlay.draw_yaw(img, '110')
    img = overlay.draw_rectangle(img, '1497')
    
    cv2.imshow('webCam',img)
    
    if (cv2.waitKey(1) == ord('s')):
        break

capture.release()
cv2.destroyAllWindows()