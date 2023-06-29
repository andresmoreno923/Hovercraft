import cv2
import numpy as np

class ImageCropped:
    def __init__(self, w, h):
        #original image size
        self.w = w
        self.h = h
        #cropped image
        self.w_ = 640
        self.h_ = 480

    def scale(self, valor):
        max_orig = 1062
        min_orig = 1923
        max_escala = 1
        min_escala = -1
        escala = (max_escala - min_escala) / (max_orig - min_orig)
        valor_escala = (valor - min_orig) * escala + min_escala
        
        if (valor_escala>1):
            valor_escala = 1.0
        elif (valor_escala<-1):
            valor_escala = -1.0
        return valor_escala

    def imgcropp(self, frame, x, y):
        x = -1*self.scale(x)
        y = -1*self.scale(y)
        new_idw = int(self.w/2 + (self.w/2 - self.w_/2)*x)
        new_idh = int(self.h/2 + (self.h/2 - self.h_/2)*y)
        return frame[new_idh - int(self.h_/2):new_idh + int(self.h_/2),new_idw - int(self.w_/2):new_idw + int(self.w_/2),:]
