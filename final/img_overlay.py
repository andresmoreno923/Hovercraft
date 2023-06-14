# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 17:55:33 2023

@author: andre
"""

import cv2
import numpy as np

class ImageOverlay:
    def __init__(self):
        self.data_s = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.color_1 = (0, 0, 255)  # rojo
        self.color_2 = (0, 165, 255)  # naranja
        self.color_3 = (56, 255, 25)  # verde
        self.icon_battery = cv2.imread('battery-icon.png', cv2.IMREAD_UNCHANGED)
        self.icon_hvc = cv2.imread('hovercraft_icon.png', cv2.IMREAD_UNCHANGED)
        self.n_cells = 1  # number of battery cells
        self.max_bat_lvl = 4.2  # maximum battery voltage
        self.min_bat_lvl = 3.6  # minimum battery voltage
        self.diff_batt = self.max_bat_lvl - self.min_bat_lvl
        self.low_lvl_bat = 0.8  # 20% battery capacity
        self.mod_lvl_bat = 0.25  # 75% battery capacity
        

    def escalar_joystick(self, valor):
        max_orig = 1062
        min_orig = 1923
        max_escala = 100
        min_escala = -100
        escala = (max_escala - min_escala) / (max_orig - min_orig)
        valor_escala = (valor - min_orig) * escala + min_escala
        return int(valor_escala)

    def draw_rectangle(self, img, data):
        data_j = -1 * self.escalar_joystick(float(data))
        img_h, img_w, _ = img.shape
        pt1 = (img_w - 40, int(img_h / 2 - 100))  # Esquina superior izquierda x - y
        pt2 = (img_w - 10, int(img_h / 2 + 100))  # Esquina inferior derecha
        img = cv2.rectangle(img, pt1, pt2, (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
        cv2.putText(img, '__', (img_w - 40, int(img_h / 2) + data_j), self.font, 1, self.color_3, 1)
        cv2.putText(img, str(-1 * data_j), (img_w - 60, int(img_h / 2) + data_j), self.font, 0.5, self.color_3, 1)
        return img

    def draw_yaw(self, img, data):
        data = float(data)
        n = 20
        img_h, img_w, _ = img.shape
        idx = int(img_w / 2)
        indx_ = np.linspace(data - 30, data + 30, 61)
        indx__ = np.linspace(-30, 30, 61)
        i = 0
        for indx in indx_:
            if not (indx % 5):
                cv2.putText(img, '|', (int(idx + n * indx__[i]), 20), self.font, 0.5, self.color_3, 1)
                cv2.putText(img, str(indx), (int(idx + n * indx__[i]), 40), self.font, 0.4, self.color_3, 1)
            i = i + 1
        return img

    def change_color(self, img, color):
        alpha_channel = img[:, :, 3]
        color_channels = img[:, :, :3]

        green_mask = np.logical_and(color_channels[:, :, 1] > 0, color_channels[:, :, 0] > 0, color_channels[:, :, 2] > 0)

        if color == self.color_1:
            color_channels[green_mask, 0] = 0
            color_channels[green_mask, 1] = 0
            color_channels[green_mask, 2] = 255
        elif color == self.color_2:
            color_channels[green_mask, 0] = 0
            color_channels[green_mask, 1] = 165
            color_channels[green_mask, 2] = 255
        elif color == self.color_3:
            color_channels[green_mask, 0] = 56
            color_channels[green_mask, 1] = 255
            color_channels[green_mask, 2] = 25

        return cv2.merge((color_channels, alpha_channel))

    def lvl_bat(self, txt):
        if float(txt) <= self.n_cells * (self.max_bat_lvl - self.low_lvl_bat * self.diff_batt):
            color_txt = self.color_1
        elif float(txt) <= self.n_cells * (self.max_bat_lvl - self.mod_lvl_bat * self.diff_batt):
            color_txt = self.color_2
        elif float(txt) > self.n_cells * (self.max_bat_lvl - self.mod_lvl_bat * self.diff_batt):
            color_txt = self.color_3  # more than 80% of the maximum battery
        return color_txt

    def add_transparent_image(self, bg, txt='0', cl=1):
        
        bg_h, bg_w, bg_channels = bg.shape
        
        if cl:
            icon = self.icon_battery
            txt_1='V'
            color_txt = self.lvl_bat(txt)
            icon = self.change_color(icon, color_txt)
            y_offset = 20
        else:
            icon = self.icon_hvc
            txt_1='m/s'
            color_txt = self.color_3
            y_offset = bg_w - 150
        
        txt = np.round(float(txt), 2)
        fg_h, fg_w, fg_channels = icon.shape
        x_offset = int(0.75*(bg_h))
        bg_section = bg[x_offset:x_offset + fg_h, y_offset:y_offset + fg_w, :]
        fg_colors = icon[:, :, :3]
        alpha_channel = icon[:, :, 3] / 255
        alpha_mask = np.dstack((alpha_channel, alpha_channel, alpha_channel))

        try:
            composite = bg_section * (1 - alpha_mask) + fg_colors * alpha_mask
        except ValueError:
            return

        bg[x_offset:x_offset + fg_h, y_offset:y_offset + fg_w, :] = composite

        cv2.putText(bg, str(txt) + str(txt_1), (y_offset + 50, x_offset + 30), self.font, 0.7, color_txt, 1)
        return bg
    def add_overlay(self, img, data):
        
        img = self.add_transparent_image(img, txt=data[6], cl=1)
        img = self.add_transparent_image(img, txt=data[5], cl=0)
        img = self.draw_yaw(img, data[4])
        img = self.draw_rectangle(img, data[1])
        
        return img
        
