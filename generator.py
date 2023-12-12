from can_parser import CAN_parser
from time import time
from config import configParam

class Update_CAN(object):
    def __init__(self, vehicle='IONIQ19'):
        # Set CAN Parser
        if vehicle=='IONIQ19':
            self.can_msg_list = ['HEV_PC4', 'SAS11', 'ESP12'] # KMU
            self.can_signal_list = [
                'LAT_ACCEL',
                'CR_Ems_VehSpd_Kmh',
                'SAS_Speed',
            ]
        elif vehicle=='NE':
            raise NotImplementedError
            self.can_msg_list = [] # KMU
            self.can_signal_list = [
                '',
                '',
                '',
            ]
            pass
        
        self.can_parser = CAN_parser(
                vehicle=vehicle,
                can_msg_list = self.can_msg_list,
                )
        
        self.latest_signal_dic = {}
        
        # self.sampling_time = configParam['TimeStep']
        # self.reset()
        
    def run(self):
        for data_dic, data_time in self.can_parser.get_can_data(self.can_signal_list):
            yield data_dic
    
