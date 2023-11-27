import multiprocessing
from multiprocessing import shared_memory
import os
import argparse
import numpy as np
import sys
from time import time

from discriminator import DiscriminatorCorner
from generator import Generator_Input

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

def run_discriminator(flag_info, stop_event):
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)

    discriminator = DiscriminatorCorner()
    
    for corner_flag in discriminator.run():
        if stop_event.is_set():
            break
        flag[0] = corner_flag
    
    flag_mem.close()
    
def generate_input(flag_info, u_info, t_info, stop_event):
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
    
    u_mem = shared_memory.SharedMemory(name=u_info['name'])
    u = np.ndarray(u_info['shape'], dtype=u_info['dtype'], buffer=u_mem.buf)
    
    t_mem = shared_memory.SharedMemory(name=t_info['name'])
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    t[0, 0] = -1

    generator = Generator_Input()
    
    while True:
        if stop_event.is_set():
            break
        while time() - generator.time < generator.sampling_time:
            pass
        # print(flag, t, end='\r')        
        if flag:
            if t[0, 0] == -1:
                # print("RRRRRRRRRRRRRRRRRRRRR")
                u_cur, u_idx, t_cur = generator.reset()
            else:
                # print("UUUUUUUUUUUUUUUUUUUUU")
                u_cur, u_idx, t_cur = generator.update()
            
            if u_idx < 500:
                t[0, 0] = t_cur
                u[0, 0, u_idx] = u_cur
            
            if (u_idx > 5) and (u_idx < 499):
                print(t_cur)
                print(t[0, 0])
                print(u[0, 0, u_idx-5:u_idx+5])
                
    flag_mem.close()
    u_mem.close()
    t_mem.close()

def main():
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
    
    # define shared input u
    u_init = np.zeros((1, 1, 500), dtype=np.float32)
    u_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=u_init.nbytes)
    u_info = {
        'name':u_mem.name,
        'dtype':u_init.dtype,
        'shape':u_init.shape,
    }
    
    u = np.ndarray(u_info['shape'], dtype=u_info['dtype'], buffer=u_mem.buf)
    u = u_init
    del u_init
    
    # define shared input t
    t_init = np.ones((1, 1), dtype=np.float32) * -1
    t_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=t_init.nbytes)
    t_info = {
        'name':t_mem.name,
        'dtype':t_init.dtype,
        'shape':t_init.shape,
    }
    
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    t = t_init
    del t_init
    print(t)
    
    
    print("[INFO] Main thread started.")
    multiproc_settings = {'DiscriminatorCorner': {'target': run_discriminator,
                                        'args': (flag_info, stop_event)},
                        'GeneratorInput': {'target': generate_input,
                                        'args': (flag_info, u_info, t_info, stop_event)},
                        }
    
    for key, value in multiproc_settings.items():
        proc = multiprocessing.Process(target=value['target'], args=value['args'])
        procs.append(proc)
    print(t)
        
    for proc in procs:
        proc.start()
    print(t)
        
    terminate_signal = input("[REQUEST] Press 'Enter' if you want to terminate every processes.\n\n")
    while terminate_signal != '':
        print("[REQUEST] Invalid input! Press 'Enter'")
        terminate_signal = input()

    stop_event.set()        

    for proc in procs:
        proc.join()
    
    flag_mem.close()
    flag_mem.unlink()
    u_mem.close()
    u_mem.unlink()
    t_mem.close()
    t_mem.unlink()

if __name__ == '__main__':
    main()
