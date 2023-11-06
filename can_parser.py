import os
import can
import cantools

class Can_parser:
    def __init__(self, can_db_path, can_data_name):
        self.can_db_path = can_db_path
        self.can_data_name = can_data_name
        
    def get_can_data(self):
        C_db = cantools.database.load_file(self.can_db_path)
        
        db_msg=[]
        print(C_db.messages)
        for msg in C_db.messages:
            db_msg.append(msg)
        
        can_data_dict={self.can_data_name[i] : None for i in range(len(self.can_data_name))}
        # print(can_data_dict)
        
        filters = [{"can_id" : db_msg[i].frame_id, "can_mask": 0xFFFFFFF} for i in range(len(db_msg))]
        print(filters)
    
if __name__ == '__main__':
    can_db_path=os.path.join(os.path.dirname(__file__), 'NE_CANdb_v2', '230518_NE1_2021_FD_C_v2.dbc')
    can_msg = ['VCU_AccPedDepVal']
    tmp = Can_parser(can_db_path=can_db_path, can_data_name=can_msg).get_can_data()