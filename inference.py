import tensorflow as tf
from model import get_origin_model
from multiprocessing import shared_memory
import numpy as np
import os
from glob import glob

class TFlite_model(object):
    def __init__(self, model_path):
        tflite_path = glob(os.path.join(model_path, 'best_*.tflite'))[0]
        self.interpreter = tf.lite.Interpreter(model_path=tflite_path)
        self.interpreter.allocate_tensors()
    
        self.input_b_index = self.interpreter.get_input_details()[0]['index']
        self.input_t_index = self.interpreter.get_input_details()[1]['index']
        self.output_index = self.interpreter.get_output_details()[0]['index']
        
    def __call__(self, input_):
        self.interpreter.set_tensor(self.input_b_index, input_[0])
        self.interpreter.set_tensor(self.input_t_index, input_[1])
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(self.output_index)
        
        return pred


def inference(u_info, t_info, x_info, stop_event):
    # flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    # flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
    
    u_mem = shared_memory.SharedMemory(name=u_info['name'])
    u = np.ndarray(u_info['shape'], dtype=u_info['dtype'], buffer=u_mem.buf)
    
    t_mem = shared_memory.SharedMemory(name=t_info['name'])
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    
    x_mem = shared_memory.SharedMemory(name=x_info['name'])
    x = np.ndarray(x_info['shape'], dtype=x_info['dtype'], buffer=x_mem.buf)
    
    model_path = os.path.dirname(__file__, 'roll_model')

    model = get_origin_model(model_path)
    model = TFlite_model(model_path)
    
    while True:
        if stop_event.is_set():
            break
        
        if not t[0, 0] == -1:
            while cur_t == prev_t:
                cur_t = t[0, 0].copy()
            
            output_ = model([u.copy(), t.copy()])
            
            x[:, :] = output_.copy()
                
            prev_t = cur_t.copy()
                
    u_mem.close()
    t_mem.close()
    x_mem.close()