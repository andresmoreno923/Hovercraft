# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 04:03:21 2023

@author: andre
"""


import cv2
import numpy as np
import math
import numba as nb


@nb.njit(fastmath=True, parallel=True)
def met_lat_long(img, R, top, left):
    img_valid = img[top:int(top + 2 * R+1), left:int(left +2 * R+1)]
    m, n, k = img_valid.shape[:3]
    result = np.zeros((m, n, k), dtype=np.float32)
    f = R * 2 / math.pi
    
    for i in nb.prange(m):
        for j in nb.prange(n):
            u = j-R
            v = R-i
            r = math.sqrt(u*u+v*v)
            
            if r == 0:
                fi = 0
            elif u >= 0:
                fi = math.asin(v/r)
            else:
                fi = math.pi - math.asin(v/r)
                
            theta = r / f
            
            x = f * math.sin(theta) * math.cos(fi)
            y = f * math.sin(theta) * math.sin(fi)
            z = f * math.cos(theta)

            #Sita longitud, fai latitud
            rr= math.sqrt(x * x + z * z)
            sita = math.pi / 2 - math.atan( y /rr)
            
            if(z>=0):
                fai = math.acos(x/rr)
            else:
                fai= math.pi - math.acos(x/rr)

            xx = round(f*sita)
            yy = round(f*fai)

            if ((xx < 1) | (yy < 1) | (xx > m) | (yy > n)):
                continue;

            result[xx,yy,:] = img_valid[i, j, :]
            
    return result
    #return cv2.flip(result,1)

@nb.njit(fastmath=True, parallel=True)
def met_lat_long2(img, R, top, left):
    img_valid = img[top:int(top + 2 * R+1), left:int(left +2 * R+1)]
    m, n, k = img_valid.shape[:3]
    result = np.zeros((m, n, k), dtype=np.float32)
    f = R * 2 / math.pi
    
    for i in nb.prange(m):
        for j in nb.prange(n):
            u = j-R
            v = R-i
            r = math.sqrt(u*u+v*v)
            
            if r == 0:
                fi = 0
            elif u >= 0:
                fi = math.asin(v/r)
            else:
                fi = math.pi - math.asin(v/r)
                
            theta = r / f
            
            x = f * math.sin(theta) * math.cos(fi)
            y = f * math.sin(theta) * math.sin(fi)
            z = f * math.cos(theta)

            #Sita longitud, fai latitud
            rr= math.sqrt(x * x + z * z)
            sita = math.pi / 2 - math.atan( y /rr)
            
            if(z>=0):
                fai = math.acos(x/rr)
            else:
                fai= math.pi - math.acos(x/rr)

            xx = round(f*sita)
            yy = round(f*fai)

            if ((xx < 1) | (yy < 1) | (xx > m) | (yy > n)):
                continue;

            result[xx,yy,:] = img_valid[i, j, :]
            
    return result
    #return cv2.flip(result,1)
 

def filter_(img, n):
    return cv2.medianBlur(img, n)


def resize_frame(frame, w, h):
    new_img = cv2.resize(frame, (w, h), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
    return new_img



