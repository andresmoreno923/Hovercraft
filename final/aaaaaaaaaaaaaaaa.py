from wifi import Cell, Scheme

def connect_to_wifi(ssid, password):
    target_network = None
    cells = Cell.all('wlan0')
    
    for cell in cells:
        print(cell.ssid)
        if cell.ssid == ssid:
            target_network = cell
            break
    scheme = Scheme.for_cell('wlan0',ssid, target_network, password)
    scheme.activate()
#     if target_network:
#         scheme = Scheme.for_cell('wlan0',ssid, target_network, password)
#         
#         if scheme:
#             scheme.activate()
#             print('conexion exitosa a :', ssid)
#         else:
#             print('no se encontro la red',ssid)
#     else:
#         print('No se encontro la red')
#         
wifi_ssid = 'RED_PC'
wifi_password = 'andres1992'

connect_to_wifi(wifi_ssid, wifi_password)