# -*- coding: utf-8 -*-
"""
Created on Tue Jun 20 14:07:30 2023

@author: andre
"""

import pywifi
from pywifi import const


ssid = 'UbeeE5CD-5G'
        

wifi = pywifi.PyWiFi()  # Inicializar el objeto PyWiFi
ifaces = wifi.interfaces()  # Obtener la interfaz WiFi

if len(ifaces) == 0:
    print('No wifi')
else:
    iface = ifaces[0]  # Usar la primera interfaz WiFi
    iface.scan()  # Escanear las redes WiFi disponibles
    results = iface.scan_results()  # Obtener los resultados del escaneo

    for result in results:
        
        if (result.ssid == ssid):
            print(ssid,': ',result.signal, type(result.signal))



