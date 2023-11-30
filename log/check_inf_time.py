import numpy as np
import os

time_arr = np.load(os.path.join(os.path.dirname(__file__), 'lateral_inf_time.npy'))
time_arr = time_arr[1:]

print(f'평균: {np.mean(time_arr)} sec / 표준편차: {np.std(time_arr)} sec')