import os
import sys
import can
import cantools
import csv

class CAN_parser:
    def __init__(self, vehicle='IONIQ19', can_msg_list=[]):
        if vehicle == 'NE':
            raise NotImplementedError
            os.system("sudo ip link set can0 up type can bitrate 500000 dbitrate 2000000 restart-ms 1000 berr-reporting on fd on sample-point .8 dsample-point .75")
            self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan',bitrate=500000, data_bitrate=2000000, fd=True, can_filters=self.filters) # HMC NE
        elif vehicle == 'IONIQ19':
            os.system("sudo ip link set can0 up type can bitrate 500000")
        else:
            raise NameError("Vehicle name is not correct.")

        self.can_db_path = os.path.join(os.path.dirname(__file__), 'dbc', 'C_CAN.dbc')

        if not os.path.isfile(self.can_db_path):
            raise FileNotFoundError(self.can_db_path)
        self.CAN_db = cantools.database.load_file(self.can_db_path)

        self.can_msg_list = can_msg_list
        #self.can_signal_list = can_signal_list
        
        for msg in self.can_msg_list:
            if not msg in [can_msg.name for can_msg in self.CAN_db.messages]:
                raise KeyError(self.can_msg_list)

        # get interested message's frame id
        self.frame_ids = []
        if len(self.can_msg_list) < 1:
            for msg in self.CAN_db.messages:
                self.frame_ids.append(msg.frame_id)
            print("Set the CAN BUS for all messages on CAN DB")
        else:
            for msg in self.CAN_db.messages:
                if msg.name in self.can_msg_list:
                    self.frame_ids.append(msg.frame_id)
            print("Set the CAN BUS for specific  messages:", self.can_msg_list)
        
        self.filters = [{"can_id" : frame_id, "can_mask": 0xFFFFFFF} for frame_id in self.frame_ids]
            
        self.can_bus = can.interface.Bus(channel = 'can0', bustype = 'socketcan', can_filters=self.filters) # KMU

            
    def get_can_data(self, can_signal_list):
        '''example
        for data_dic, data_time in parser.get_can_data(can_signal_list):
            print(time() - data_time)
            for k, v in data_dic.items():
                print(k, v)
        '''
        with self.can_bus as can_bus:
            while True:
                #can_msg = self.can_bus.recv()
                can_msg = can_bus.recv()
                can_data = self.CAN_db.decode_message(can_msg.arbitration_id, can_msg.data)
                can_time = can_msg.timestamp

                cur_keys = [key for key in can_data.keys() if key in can_signal_list]
                
                data_dic = {}
                for key in cur_keys:
                    data_dic[key] = can_data[key]

                yield data_dic, can_time
            

    def save_can_data(self, file_name, can_signal_list):
        print(f"[I] CSV file is being written...{file_name}")
        f = open(file_name, "w")
        writer = csv.writer(f)
        
        first_row = ['signal', 'values', 'data_time', 'delay_time']
        writer.writerow(first_row)

        for data_dic, data_time in self.get_can_data(can_signal_list):
            delay_time = time() - data_time
            for k, v in data_dic.items():
                writer.writerow([k, v, data_time, delay_time])

        # f.close()


if __name__ == '__main__':
    from time import time
    # can_msg_list = ['HEV_PC4', 'SAS11', 'ESP12'], # KMU
    # can_signal_list = ['CR_Ems_AccPedDep_Pc', 'CR_Brk_StkDep_Pc','SAS_Angle', 'SAS_Speed', 'LONG_ACCEL', 'LAT_ACCEL', 'YAW_RATE']
    # can_signal_list = ['VCU_01_10ms', 'IEB_01_10ms', 'SAS_01_10ms', 'IMU_01_10ms'], # HMC NE

    date = '231120'

    '''
    can_msg_list = ['ESP12'] # KMU
    can_signal_list = ['LONG_ACCEL', 'LAT_ACCEL', 'YAW_RATE']
    parser = CAN_parser(
            can_msg_list = can_msg_list,
            )
    parser.save_can_data(f'{date}_ESP12.csv', can_signal_list)
    
    '''
    can_msg_list = ['SAS11'] # KMU
    can_signal_list = ['SAS_Angle', 'SAS_Speed']
    parser = CAN_parser(
            can_msg_list = can_msg_list,
            )
    parser.save_can_data(f'{date}_SAS11.csv', can_signal_list)
