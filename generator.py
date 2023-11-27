from can_parser import CAN_parser
from time import time
from config import configParam

class Generator_Input(object):
    def __init__(self, vehicle='IONIQ19'):
        # Set CAN Parser
        self.can_msg_list = ['ESP12'] # KMU
        self.signal_ay = 'LAT_ACCEL'
        # self.can_signal_list = [self.signal_ay]
        
        self.can_parser = CAN_parser(
                vehicle=vehicle,
                can_msg_list = self.can_msg_list,
                )
        
        self.sampling_time = configParam['TimeStep']
        self.reset()
    
    def get_u(self):
        can_msg = self.can_parser.can_bus.recv()
        can_msg = self.can_parser.CAN_db.decode_message(can_msg.arbitration_id, can_msg.data)
        data = can_msg[self.signal_ay]
        
        return data
        
    def reset(self):
        self.input_t = 0.0
        self.u_idx = 0
        self.time = time()
        
        return self.get_u(), self.u_idx, self.input_t
        
    def update(self):
        self.input_t += self.sampling_time
        self.u_idx += 1
        self.time = time()
        
        return self.get_u(), self.u_idx, self.input_t
    
