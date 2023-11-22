import multiprocessing
import os
import argparse

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

def run_discriminator(shared_flag, lock, stop_event):
    discriminator = DiscriminatorCorner()
    for duration_time in discriminator.run():
        if stop_event.is_set():
                break
        shared_flag.value = duration_time
        print(f"{duration_time}       ", end='\r')
    
def main():
    procs = []
    stop_event = multiprocessing.Event()
    shared_flag = multiprocessing.Value('i', True)
    lock = multiprocessing.Lock()
    
    print("[INFO] Main thread started.")
    multiproc_settings = {'DiscriminatorCorner': {'target': run_discriminator,
                                        'args': (shared_flag, lock, stop_event)},
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

if __name__ == '__main__':
    # print(bool(multiprocessing.Value('i', True).value))
    os.system("sudo ip link set can0 up type can bitrate 500000")
    main()