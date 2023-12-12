from can_parser import CAN_parser
from time import time
from config import configParam, can_msg_list, signal_ay, signal_steer_spd, signal_veh_spd, StrGearRatio, CONVERSION_FACTOR

class Update_CAN(object):
    def __init__(self, vehicle_id=0):
        # Set CAN Parser
        self.can_msg_list = can_msg_list[vehicle_id] # KMU
        self.can_signal_list = [
                signal_ay[vehicle_id],
                signal_veh_spd[vehicle_id],
                signal_steer_spd[vehicle_id],
            ]
        
        self.can_parser = CAN_parser(
                vehicle_id=vehicle_id,
                can_msg_list = self.can_msg_list,
                )
        
        self.latest_signal_dic = {}
        
    def run(self):
        for data_dic, data_time in self.can_parser.get_can_data(self.can_signal_list):
            yield data_dic

from multiprocessing import shared_memory
import numpy as np
def stack_can(vehicle_id, ay_cur_info, s_cur_info, vx_cur_info, stop_event):
    ay_cur_mem = shared_memory.SharedMemory(name=ay_cur_info['name'])
    ay_cur = np.ndarray(ay_cur_info['shape'], dtype=ay_cur_info['dtype'], buffer=ay_cur_mem.buf)
    
    s_cur_mem = shared_memory.SharedMemory(name=s_cur_info['name'])
    s_cur = np.ndarray(s_cur_info['shape'], dtype=s_cur_info['dtype'], buffer=s_cur_mem.buf)
    
    vx_cur_mem = shared_memory.SharedMemory(name=vx_cur_info['name'])
    vx_cur = np.ndarray(vx_cur_info['shape'], dtype=vx_cur_info['dtype'], buffer=vx_cur_mem.buf)
    
    updator = Update_CAN(vehicle_id=vehicle_id)
    for data_dic in updator.run():
        if stop_event.is_set():
            break
        
        for k, v in data_dic.items():
            if k == signal_ay[vehicle_id]:
                ay_cur = v # m/s2
            elif k == signal_steer_spd[vehicle_id]:
                s_cur = (v / StrGearRatio[vehicle_id]) * CONVERSION_FACTOR['DEG2RAD']
            elif k == signal_veh_spd[vehicle_id]:
                vx_cur = v * CONVERSION_FACTOR['KPH2MPS']

    ay_cur_mem.close()
    s_cur_mem.close()
    vx_cur_mem.close()
    
    
def generate_input(flag_info, ay_info, s_vx_info, ay_cur_info, s_cur_info, vx_cur_info, t_info, stop_event):
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
    
    ay_mem = shared_memory.SharedMemory(name=ay_info['name'])
    ay = np.ndarray(ay_info['shape'], dtype=ay_info['dtype'], buffer=ay_mem.buf)
    
    s_vx_mem = shared_memory.SharedMemory(name=s_vx_info['name'])
    s_vx = np.ndarray(s_vx_info['shape'], dtype=s_vx_info['dtype'], buffer=s_vx_mem.buf)
    
    t_mem = shared_memory.SharedMemory(name=t_info['name'])
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    
    ay_cur_mem = shared_memory.SharedMemory(name=ay_cur_info['name'])
    ay_cur = np.ndarray(ay_cur_info['shape'], dtype=ay_cur_info['dtype'], buffer=ay_cur_mem.buf)
    
    s_cur_mem = shared_memory.SharedMemory(name=s_cur_info['name'])
    s_cur = np.ndarray(s_cur_info['shape'], dtype=s_cur_info['dtype'], buffer=s_cur_mem.buf)
    
    vx_cur_mem = shared_memory.SharedMemory(name=vx_cur_info['name'])
    vx_cur = np.ndarray(vx_cur_info['shape'], dtype=vx_cur_info['dtype'], buffer=vx_cur_mem.buf)
    
    get_time = 0.0
    
    while True:
        if stop_event.is_set():
            break
        while time.time() - get_time < configParam['TimeStep']:
            pass
        if flag:

            if t[0, 0] == -1:
                t_cur = 0.0
                t_idx = 0
            else:
                t_cur += configParam['TimeStep']
                t_idx += 1
            get_time = time.time()
            
            if t_idx < 500:
                t[0, 0] = t_cur
                ay[0, t_idx] = ay_cur.copy()
                s_vx[0, 0, t_idx] = s_cur.copy()
                s_vx[0, 1, t_idx] = vx_cur.copy()
            
        else:
            if t[0, 0] != -1:
                t[0, 0] = -1.
                ay = np.zeros((1, 500), dtype=np.float32)
                s_vx = np.zeros((1, 2, 500), dtype=np.float32)
                
    flag_mem.close()
    ay_mem.close()
    s_vx_mem.close()
    t_mem.close()
    ay_cur_mem.close()
    s_cur_mem.close()
    vx_cur_mem.close()
