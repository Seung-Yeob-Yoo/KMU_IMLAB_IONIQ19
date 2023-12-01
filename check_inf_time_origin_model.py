import numpy as np
import tensorflow as tf
from model import get_origin_model, get_DeepONet_Lateral
from multiprocessing import shared_memory
import numpy as np
import os
from glob import glob
import time

model = get_DeepONet_Lateral(
        num_nodes=32,
        activation='tanh',
    )
# model = TFlite_model(model_path) # for tflite model

prev_t = np.array([[-1.]], dtype=np.float32)

inf_time_list=[]
while True:
    u = np.random.rand(2,500)
    t = np.random.rand(1)
    
    start_time = time.time()
    output_ = model([u.copy(), t.copy()])
    inf_time_list.append(time.time() - start_time)
    inf_time_arr = np.array(inf_time_list)
    np.save(os.path.join(os.path.dirname(__file__), 'log','lateral_inf_time.npy'), inf_time_arr)
    