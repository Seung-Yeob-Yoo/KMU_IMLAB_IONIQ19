import numpy as np
import os

save_path = os.path.join(os.path.dirname(__file__), 'log', 'TFlite_model') # get_origin_model, TFlite_model
arr = np.load(save_path)
arr = arr[1:]
print(f'평균: {np.mean(arr)}sec / 표준편차: {np.std(arr)}sec')