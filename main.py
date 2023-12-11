import multiprocessing
from multiprocessing import shared_memory
import os
import argparse
import numpy as np
import sys
import time
import platform

from config import vehicleParam, configParam, CONVERSION_FACTOR
from discriminator import DiscriminatorCorner
from generator import Update_CAN
from inference import inference_roll, inference_lateral
from data_send import datasend

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
'''
parser = argparse.ArgumentParser(description='Inference environment setup')
parser.add_argument('--vehicle', '-v', type=str, required=True,
                    help='Which vehicle does the running vehicle belong to? (IONIQ19 or NE)')
parser.add_argument('--isSave', type=str2bool, default=False,
                    help='Save the inference results')
args = parser.parse_args()
'''

def run_discriminator(vehicle, flag_info, stop_event):
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)

    discriminator = DiscriminatorCorner(vehicle=vehicle)
    
    for corner_flag in discriminator.run():
        if stop_event.is_set():
            break
        flag[0] = corner_flag
    
    flag_mem.close()
    
def update_can(vehicle, ay_cur_info, s_cur_info, vx_cur_info, stop_event):
    ay_cur_mem = shared_memory.SharedMemory(name=ay_cur_info['name'])
    ay_cur = np.ndarray(ay_cur_info['shape'], dtype=ay_cur_info['dtype'], buffer=ay_cur_mem.buf)
    
    s_cur_mem = shared_memory.SharedMemory(name=s_cur_info['name'])
    s_cur = np.ndarray(s_cur_info['shape'], dtype=s_cur_info['dtype'], buffer=s_cur_mem.buf)
    
    vx_cur_mem = shared_memory.SharedMemory(name=vx_cur_info['name'])
    vx_cur = np.ndarray(vx_cur_info['shape'], dtype=vx_cur_info['dtype'], buffer=vx_cur_mem.buf)
    
    updator = Update_CAN(vehicle=vehicle)
    for data_dic in updator.run():
        if stop_event.is_set():
            break
        
        for k, v in data_dic.items():
            if k == 'LAT_ACCEL':
                ay_cur = v # m/s2
            elif k == 'SAS_Speed':
                s_cur = (v / vehicleParam[vehicle]['StrGearRatio']) * CONVERSION_FACTOR['DEG2RAD']
            elif k == 'CR_Ems_VehSpd_Kmh':
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
    # t[0, 0] = -1
    print(t[0][0])
    
    ay_cur_mem = shared_memory.SharedMemory(name=ay_cur_info['name'])
    ay_cur = np.ndarray(ay_cur_info['shape'], dtype=ay_cur_info['dtype'], buffer=ay_cur_mem.buf)
    
    s_cur_mem = shared_memory.SharedMemory(name=s_cur_info['name'])
    s_cur = np.ndarray(s_cur_info['shape'], dtype=s_cur_info['dtype'], buffer=s_cur_mem.buf)
    
    vx_cur_mem = shared_memory.SharedMemory(name=vx_cur_info['name'])
    vx_cur = np.ndarray(vx_cur_info['shape'], dtype=vx_cur_info['dtype'], buffer=vx_cur_mem.buf)
    
    get_time = 0.0
    times = []
    
    while True:
        if stop_event.is_set():
            break
        while time.time() - get_time < configParam['TimeStep']:
            pass
        # print(flag, t, end='\r')        
        if flag:
            times.append(time.time())
            times_array = np.array(times)
            np.save(os.path.join(os.path.dirname(__file__), 'log', 'generate.npy'), times_array)

        
            if t[0, 0] == -1:
                # print("RRRRRRRRRRRRRRRRRRRRR")
                # u_cur, t_idx, t_cur = generator.reset()
                t_cur = 0.0
                t_idx = 0
            else:
                # print("UUUUUUUUUUUUUUUUUUUUU")
                # u_cur, t_idx, t_cur = generator.update()
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

def main(vehicle):
    procs = []
    stop_event = multiprocessing.Event()

    # define shared flag
    flag_init = np.array([False], dtype=np.bool_)
    flag_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=flag_init.nbytes)
    flag_info = {
        'name':flag_mem.name,
        'dtype':flag_init.dtype,
        'shape':flag_init.shape,
    }
    
    flag = np.ndarray(flag_init.shape, dtype=flag_info['dtype'], buffer=flag_mem.buf)
    flag = flag_init
    del flag_init
    
    # define shared input ay
    ay_init = np.zeros((1, 500), dtype=np.float32)
    ay_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=ay_init.nbytes)
    ay_info = {
        'name':ay_mem.name,
        'dtype':ay_init.dtype,
        'shape':ay_init.shape,
    }
    
    ay = np.ndarray(ay_info['shape'], dtype=ay_info['dtype'], buffer=ay_mem.buf)
    ay = ay_init
    del ay_init
    
    # define shared input s, vx
    s_vx_init = np.zeros((1, 2, 500), dtype=np.float32)
    s_vx_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=s_vx_init.nbytes)
    s_vx_info = {
        'name':s_vx_mem.name,
        'dtype':s_vx_init.dtype,
        'shape':s_vx_init.shape,
    }
    
    s_vx = np.ndarray(ay_info['shape'], dtype=s_vx_info['dtype'], buffer=s_vx_mem.buf)
    s_vx = s_vx_init
    del s_vx_init
    
    # define shared input t
    t_init = np.array([[1.]], dtype=np.float32)
    t_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=t_init.nbytes)
    t_info = {
        'name':t_mem.name,
        'dtype':t_init.dtype,
        'shape':t_init.shape,
    }
    
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    t[0, 0] = -1
    del t_init
    
    # define shared output roll
    roll_init = np.zeros((1, 2), dtype=np.float32)
    roll_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=roll_init.nbytes)
    roll_info = {
        'name':roll_mem.name,
        'dtype':roll_init.dtype,
        'shape':roll_init.shape,
    }
    
    roll = np.ndarray(roll_info['shape'], dtype=roll_info['dtype'], buffer=roll_mem.buf)
    roll = roll_init
    del roll_init
    
    # define shared output lateral
    lateral_init = np.zeros((1, 2), dtype=np.float32)
    lateral_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=lateral_init.nbytes)
    lateral_info = {
        'name':lateral_mem.name,
        'dtype':lateral_init.dtype,
        'shape':lateral_init.shape,
    }
    
    lateral = np.ndarray(lateral_info['shape'], dtype=lateral_info['dtype'], buffer=lateral_mem.buf)
    lateral = lateral_init
    del lateral_init
    
    # define shared signal
    signal_init = np.zeros((1,), dtype=np.float32)
    ay_cur_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=signal_init.nbytes)
    s_cur_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=signal_init.nbytes)
    vx_cur_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=signal_init.nbytes)
    ay_cur_info = {
        'name':ay_cur_mem.name,
        'dtype':signal_init.dtype,
        'shape':signal_init.shape,
    }
    s_cur_info = {
        'name':s_cur_mem.name,
        'dtype':signal_init.dtype,
        'shape':signal_init.shape,
    }
    vx_cur_info = {
        'name':vx_cur_mem.name,
        'dtype':signal_init.dtype,
        'shape':signal_init.shape,
    }
    
    ay_cur = np.ndarray(signal_init.shape, dtype=signal_init.dtype, buffer=ay_cur_mem.buf)
    s_cur = np.ndarray(signal_init.shape, dtype=signal_init.dtype, buffer=s_cur_mem.buf)
    vx_cur = np.ndarray(signal_init.shape, dtype=signal_init.dtype, buffer=vx_cur_mem.buf)
    ay_cur = signal_init
    s_cur = signal_init
    vx_cur = signal_init
    del signal_init
    
    print("[INFO] Main thread started.")
    multiproc_settings = {'DiscriminatorCorner': {'target': run_discriminator,
                                        'args': (vehicle, flag_info, stop_event)},
                        'UpdateCan': {'target':update_can,
                                        'args': (vehicle, ay_cur_info, s_cur_info, vx_cur_info, stop_event)},
                        'GeneratorInput': {'target': generate_input,
                                        'args': (flag_info, ay_info, s_vx_info, ay_cur_info, s_cur_info, vx_cur_info, t_info, stop_event)},
                         'InferenceRoll': {'target': inference_roll,
                            'args': (ay_info, t_info, roll_info, stop_event)},
                         'InferenceLateral': {'target': inference_lateral,
                             'args': (s_vx_info, t_info, lateral_info, stop_event)},
                         'Data Send' : {'target': datasend,
                                       'args' : (flag_info, roll_info, lateral_info, stop_event)
                                        }
                        # 'Visualize': {'target': visualize,
                           #'args': (flag_info, roll_info, lateral_info, stop_event)},
                        }
    
    for key, value in multiproc_settings.items():
        proc = multiprocessing.Process(target=value['target'], args=value['args'])
        procs.append(proc)
        
    for proc in procs:
        proc.start()
    
    time.sleep(5)
    terminate_signal = input("[REQUEST] Press 'Enter' if you want to terminate every processes.\n\n")
    while terminate_signal != '':
        print("[REQUEST] Invalid input! Press 'Enter'")
        terminate_signal = input()

    stop_event.set()        

    for proc in procs:
        proc.join()
    
    flag_mem.close()
    flag_mem.unlink()
    ay_mem.close()
    ay_mem.unlink()
    s_vx_mem.close()
    s_vx_mem.unlink()
    t_mem.close()
    t_mem.unlink()
    roll_mem.close()
    roll_mem.unlink()
    lateral_mem.close()
    lateral_mem.unlink()
    ay_cur_mem.close()
    ay_cur_mem.unlick()
    s_cur_mem.close()
    s_cur_mem.unlick()
    vx_cur_mem.close()
    vx_cur_mem.unlick()

if __name__ == '__main__':
    if platform.system() == 'Linux':
        os.system(f"sudo chmod 777 /dev/ttyS0")
    vehicle = 'IONIQ19'
    main(vehicle)
