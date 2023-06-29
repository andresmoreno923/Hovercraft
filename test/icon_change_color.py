# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 19:10:28 2023

@author: andre
"""

import cv2
import numpy as np

icon_ssid = cv2.imread('hovercraft_icon.png', cv2.IMREAD_UNCHANGED)

color = [56,255,25]


icon_ssid[:,:,0] = np.where(icon_ssid[:,:,0] == 0, 56, icon_ssid[:,:,0])
icon_ssid[:,:,1] = np.where(icon_ssid[:,:,1] == 0, 255, icon_ssid[:,:,1])
icon_ssid[:,:,2] = np.where(icon_ssid[:,:,2] == 0, 25, icon_ssid[:,:,2])


cv2.imwrite('hovercraft_icon.png', icon_ssid)

