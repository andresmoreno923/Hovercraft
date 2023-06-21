# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:07:30 2023

@author: andre
"""

import pywifi
from pywifi import const


wifi = pywifi.PyWiFi()  # Inicializar el objeto PyWiFi
ifaces = wifi.interfaces()  # Obtener la interfaz WiFi

if len(ifaces) == 0:
    print("No se encontró ninguna interfaz WiFi.")


iface = ifaces[0]  # Usar la primera interfaz WiFi

iface.scan()  # Escanear las redes WiFi disponibles
resultados = iface.scan_results()  # Obtener los resultados del escaneo

for resultado in resultados:
    ssid = resultado.ssid
    bssid = resultado.bssid
    potencia = resultado.signal

    print(f"SSID: {ssid}, BSSID: {bssid}, Potencia: {potencia} dBm")


