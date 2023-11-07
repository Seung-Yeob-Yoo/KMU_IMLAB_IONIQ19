import os
import sys
import can
import cantools

class Can_parser:
    def __init__(self, vehicle, can_db_path, can_data_name):
        os.system("sudo ip link set can0 up type can bitrate 500000")
        self.vehicle = vehicle
        self.can_msg_list={'IONIQ19':['HEV_PC4', 'SAS11', 'ESP12'], # KMU
        'NE':['VCU_01_10ms', 'IEB_01_10ms', 'SAS_01_10ms', 'IMU_01_10ms'], # HMC NE
        }
        self.can_data_name = can_data_name
        self.C_db = cantools.database.load_file(can_db_path)
        
        self.db_msg=[]
        for msg in self.C_db.messages:
            if msg.name in self.can_msg_list[self.vehicle]:
                self.db_msg.append(msg)
        
        self.can_data_dict={self.can_data_name[i] : None for i in range(len(self.can_data_name))}
        
        self.filters = [{"can_id" : self.db_msg[i].frame_id, "can_mask": 0xFFFFFFF} for i in range(len(self.db_msg))]
        
        if vehicle == 'NE':
            self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan',bitrate=500000, data_bitrate=2000000, fd=True, can_filters=self.filters) # HMC NE
        elif vehicle == 'IONIQ19':
            self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters=self.filters) # KMU
        else:
            raise NameError("Vehicle name is not correct.")
        
    def get_can_data(self):
        while True:
            can_msg = self.can_bus.recv()
            
            for msg in self.db_msg:
                if can_msg.arbitration_id == msg.frame_id:
                    can_dict = self.C_db.decode_message(can_msg.arbitration_id, can_msg.data)
                    print(self.can_data_name)
                    can_dict = {k: v for k, v in can_dict.items() if k in self.can_data_name}

                    for k, v in can_dict.items():
                        self.can_data_dict[k] = v
            
            if 'not' in str(self.can_data_dict[self.can_data_name[0]]):
                self.can_data_dict[self.can_data_name[0]] = 0.0
            elif 'fully' in str(self.can_data_dict[self.can_data_name[0]]):
                self.can_data_dict[self.can_data_name[0]] = 100.0

            if None in self.can_data_dict.values():
                continue
            
            yield self.can_data_dict
            self.can_data_dict={self.can_data_name[i] : None for i in range(len(self.can_data_name))}

if __name__ == '__main__':
    vehicle = 'IONIQ19'
    can_db_path=os.path.join(os.path.dirname(__file__), 'dbc', 'C_CAN.dbc')
    can_msg = ['CR_Ems_AccPedDep_Pc', 'CR_Brk_StkDep_Pc']
    for i in Can_parser(vehicle=vehicle, can_db_path=can_db_path, can_data_name=can_msg).get_can_data():
        print(i)
