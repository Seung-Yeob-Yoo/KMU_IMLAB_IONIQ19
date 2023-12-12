import tensorflow as tf
from multiprocessing import shared_memory
import numpy as np
import os
from glob import glob
import time

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


def inference_roll(u_info, t_info, x_info, stop_event):
    u_mem = shared_memory.SharedMemory(name=u_info['name'])
    u = np.ndarray(u_info['shape'], dtype=u_info['dtype'], buffer=u_mem.buf)
    
    t_mem = shared_memory.SharedMemory(name=t_info['name'])
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    
    x_mem = shared_memory.SharedMemory(name=x_info['name'])
    x = np.ndarray(x_info['shape'], dtype=x_info['dtype'], buffer=x_mem.buf)
    
    model_path = os.path.join(os.path.dirname(__file__), 'roll_model')

    model = TFlite_model(model_path) # for tflite model

    prev_t = np.array([[-1.]], dtype=np.float32)
    
    inf_time_list = []
    while True:
        if stop_event.is_set():
            break
        
        cur_t = t[0, 0].copy()
        while (cur_t == prev_t) or (cur_t == -1):
            if cur_t == -1:
                x[0][0] = 0.
                x[0][1] = 0.
            cur_t = t[0, 0].copy()
        
        output_ = model([u.copy(), t.copy()])
        x[:, :] = output_.copy() # for tflite model
        
        inf_time_list.append(time.time())
        inf_time_arr = np.array(inf_time_list)
        np.save(os.path.join(os.path.dirname(__file__), 'log', 'inf_time_roll'), inf_time_arr)
        
        prev_t = cur_t.copy()

    u_mem.close()
    t_mem.close()
    x_mem.close()

def inference_lateral(u_info, t_info, x_info, stop_event):
    u_mem = shared_memory.SharedMemory(name=u_info['name'])
    u = np.ndarray(u_info['shape'], dtype=u_info['dtype'], buffer=u_mem.buf)
    
    t_mem = shared_memory.SharedMemory(name=t_info['name'])
    t = np.ndarray(t_info['shape'], dtype=t_info['dtype'], buffer=t_mem.buf)
    
    x_mem = shared_memory.SharedMemory(name=x_info['name'])
    x = np.ndarray(x_info['shape'], dtype=x_info['dtype'], buffer=x_mem.buf)
    
    model_path = os.path.join(os.path.dirname(__file__), 'lateral_model')

    model = TFlite_model(model_path) # for tflite model

    prev_t = np.array([[-1.]], dtype=np.float32)

    inf_time_list=[]

    while True:
        if stop_event.is_set():
            break

        cur_t = t[0, 0].copy()
        while (cur_t == prev_t) or (cur_t == -1):
            if cur_t == -1:
                x[0][0] = 0.
                x[0][1] = 0.
            cur_t = t[0, 0].copy()
            
        output_ = model([u.copy(), t.copy()])
        
        x[:, :] = output_.copy() # for tflite model
        
        inf_time_list.append(time.time())
        inf_time_arr = np.array(inf_time_list)
        np.save(os.path.join(os.path.dirname(__file__), 'log', 'inf_time_lateral'), inf_time_arr)
        
        prev_t = cur_t.copy()

    u_mem.close()
    t_mem.close()
    x_mem.close()
