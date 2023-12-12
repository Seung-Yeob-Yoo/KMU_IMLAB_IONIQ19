import numpy as np
from multiprocessing import shared_memory
import socket
import time
import serial

def datasend(flag_info, roll_info, lateral_info, stop_event, uart=False):
    if uart:
        jet_tx = serial.Serial(
        port ='/dev/ttyS0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE)  
        
    else:
        host = 'localhost'
        port=8888
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
    
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
    
    roll_mem = shared_memory.SharedMemory(name=roll_info['name'])
    roll = np.ndarray(roll_info['shape'], dtype=roll_info['dtype'], buffer=roll_mem.buf)
    
    lat_mem = shared_memory.SharedMemory(name=lateral_info['name'])
    lat = np.ndarray(lateral_info['shape'], dtype=lateral_info['dtype'], buffer=lat_mem.buf)

    while True:
        if stop_event.is_set():
            sock.close()
            break
        
        if uart:
            data_to_send = np.array([flag[0], roll[0][0], roll[0][1], lat[0][0], lat[0][1]]).tobytes()
            jet_tx.write(data_to_send)
        else:
            # data = f'str,{flag[0]},{roll[0][0]},{roll[0][1]},{lat[0][0]},{lat[0][1]},end,'
            data = f'str,{roll[0][0]},{roll[0][1]},{lat[0][0]},{lat[0][1]},end,'
            sock.send(data.encode())
        time.sleep(0.01)
        
    sock.close()