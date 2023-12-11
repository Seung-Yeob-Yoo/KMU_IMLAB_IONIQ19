import numpy as np
import tensorflow as tf
from model import get_origin_model, get_DeepONet_Lateral
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
        print(self.interpreter.get_input_details())
        self.output_index = self.interpreter.get_output_details()[0]['index']
        
    def __call__(self, input_):
        self.interpreter.set_tensor(self.input_b_index, input_[0])
        self.interpreter.set_tensor(self.input_t_index, input_[1])
        self.interpreter.invoke()
        pred = self.interpreter.get_tensor(self.output_index)
        
        return pred


# model = get_DeepONet_Lateral(
        # num_nodes=32,
        #activation='tanh',
    # )
model_path = os.path.join(os.path.dirname(__file__), 'lateral_model')
model = TFlite_model(model_path) # for tflite model

prev_t = np.array([[-1.]], dtype=np.float32)

inf_time_list=[]
while True:
    u = np.random.rand(2,500).astype(np.float32).reshape(1, 2, 500)
    t = np.random.rand(1).astype(np.float32).reshape(1, 1)
    
    start_time = time.time()
    output_ = model([u.copy(), t.copy()])
    inf_time_list.append(time.time() - start_time)
    inf_time_arr = np.array(inf_time_list)
    np.save(os.path.join(os.path.dirname(__file__), 'log','gpu_model.npy'), inf_time_arr)
    if len(inf_time_list) >1000:
        break
