import multiprocessing
from multiprocessing import shared_memory
import os
import argparse
import numpy as np
import sys

from discriminator import DiscriminatorCorner

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

def run_discriminator(shared_flag, shared_memory_name, stop_event):
    c = shared_memory.SharedMemory(name=shared_memory_name)
    shared_flag = np.ndarray((1,), dtype=np.bool_, buffer=c.buf)

    discriminator = DiscriminatorCorner()
    
    for corner_flag in discriminator.run():
        if stop_event.is_set():
            c.close()
            break
        shared_flag[0] = corner_flag
    
def generate_input(shared_flag, shared_memory_name, stop_event):
    c = shared_memory.SharedMemory(name=shared_memory_name)
    shared_flag = np.ndarray((1,), dtype=np.bool_, buffer=c.buf)

    while True:
        if stop_event.is_set():
            c.close()
            break
        print(shared_flag, end='\r')

def main():
    procs = []
    stop_event = multiprocessing.Event()

    shared_flag_init = np.array([False])
    shared_mem = multiprocessing.shared_memory.SharedMemory(create=True, size=shared_flag_init.nbytes)
    shared_memory_name = shared_mem.name
    shared_flag = np.ndarray(shared_flag_init.shape, dtype=shared_flag_init.dtype, buffer=shared_mem.buf)
    shared_flag = shared_flag_init
    del shared_flag_init
    
    print("[INFO] Main thread started.")
    multiproc_settings = {'DiscriminatorCorner': {'target': run_discriminator,
                                        'args': (shared_flag, shared_memory_name, stop_event)},
                          'GeneratorInput': {'target': generate_input,
                                        'args': (shared_flag, shared_memory_name, stop_event)},
                        }
    
    for key, value in multiproc_settings.items():
        proc = multiprocessing.Process(target=value['target'], args=value['args'])
        procs.append(proc)
        
    for proc in procs:
        proc.start()
        
    terminate_signal = input("[REQUEST] Press 'Enter' if you want to terminate every processes.\n\n")
    while terminate_signal != '':
        print("[REQUEST] Invalid input! Press 'Enter'")
        terminate_signal = input()

    stop_event.set()        

    for proc in procs:
        proc.join()
    
    shared_mem.close()
    shared_mem.unlink()

if __name__ == '__main__':
    main()
