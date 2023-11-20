import os
import sys
import can
import cantools

class SAS_parser:
    def __init__(self, vehicle, can_db_path):
        self.vehicle = vehicle
        self.can_msg_list={'IONIQ19':['SAS11'], # KMU
        # 'NE':['VCU_01_10ms', 'IEB_01_10ms', 'SAS_01_10ms', 'IMU_01_10ms'], # HMC NE
        }
        self.C_db = cantools.database.load_file(can_db_path)
        
        for msg in self.C_db.messages:
            if msg.name in self.can_msg_list[self.vehicle]:
                self.db_msg = msg
        
        self.filters = [{"can_id" : self.db_msg.frame_id, "can_mask": 0xFFFFFFF}]
        
        if vehicle == 'NE':
            self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan',bitrate=500000, data_bitrate=2000000, fd=True, can_filters=self.filters) # HMC NE
        elif vehicle == 'IONIQ19':
            self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters=self.filters) # KMU
        else:
            raise NameError("Vehicle name is not correct.")
        
    def get_can_data(self):
        while True:
            can_msg = self.can_bus.recv()
            
            if can_msg.arbitration_id == self.db_msg.frame_id:
                can_dict = self.C_db.decode_message(can_msg.arbitration_id, can_msg.data)
                # can_dict = {k: v for k, v in can_dict.items() if k in self.can_data_name[vehicle]}
            
            yield can_dict

if __name__ == '__main__':
    vehicle = 'IONIQ19'
    can_db_path=os.path.join(os.path.dirname(__file__), 'dbc', 'C_CAN.dbc')
    # can_msg = ['VCU_AccPedDepVal']
    for i in SAS_parser(vehicle=vehicle, can_db_path=can_db_path).get_can_data():
        print(i)