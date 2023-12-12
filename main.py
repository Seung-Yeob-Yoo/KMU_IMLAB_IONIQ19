import multiprocessing
from multiprocessing.shared_memory import SharedMemory
import os
import argparse
import numpy as np
import time
from discriminator import run_discriminator
from generator import stack_can, generate_input
from inference import inference_roll, inference_lateral
from communication import data_send

def main(vehicle_id, com_id):
    procs = []
    stop_event = multiprocessing.Event()

    # define shared flag
    flag_init = np.array([False], dtype=np.bool_)
    flag_mem = SharedMemory(create=True, size=flag_init.nbytes)
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
    ay_mem = SharedMemory(create=True, size=ay_init.nbytes)
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
    s_vx_mem = SharedMemory(create=True, size=s_vx_init.nbytes)
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
    t_mem = SharedMemory(create=True, size=t_init.nbytes)
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
    roll_mem = SharedMemory(create=True, size=roll_init.nbytes)
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
    lateral_mem = SharedMemory(create=True, size=lateral_init.nbytes)
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
    ay_cur_mem = SharedMemory(create=True, size=signal_init.nbytes)
    s_cur_mem = SharedMemory(create=True, size=signal_init.nbytes)
    vx_cur_mem = SharedMemory(create=True, size=signal_init.nbytes)
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
    multiproc_settings = {
        'DiscriminatorCorner': 
            {
            'target': run_discriminator,
            'args': (vehicle_id, flag_info, stop_event)
            },
        'StackCan': 
            {
            'target':stack_can,
            'args': (vehicle_id, ay_cur_info, s_cur_info, vx_cur_info, stop_event)
            },
        'GeneratorInput': 
            {
            'target': generate_input,
            'args': (flag_info, ay_info, s_vx_info, ay_cur_info, s_cur_info, vx_cur_info, t_info, stop_event)
            },
        'InferenceRoll': 
            {
            'target': inference_roll,
            'args': (ay_info, t_info, roll_info, stop_event)
            },
        'InferenceLateral': 
            {
            'target': inference_lateral,
            'args': (s_vx_info, t_info, lateral_info, stop_event)
            },
        'DataSend' : 
            {
            'target': data_send,
            'args' : (flag_info, roll_info, lateral_info, com_id, stop_event)
            }
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


def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

parser = argparse.ArgumentParser(description='Inference environment setup')
parser.add_argument('--vehicle', '-v', type=str, required=True,
                    help='Which vehicle does the running vehicle belong to? (IONIQ19 or NE)')
parser.add_argument('--communication', '-c', type=str, required=True,
                    help='Which communication method use? (UART or TCP/IP)')
args = parser.parse_args()

from config import available_vehicles, available_communications
if __name__ == '__main__':
    com_id = available_communications[args.communication]
    vehicle_id = available_vehicles[args.vehicle]
    
    if com_id == 0:
        os.system(f"sudo chmod 777 /dev/ttyS0")
        
    main(vehicle_id, com_id)
