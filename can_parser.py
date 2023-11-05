import can
import cantools

class Can_parser:
    def __init__(self, can_db_path, can_msg):
        self.can_db_path = can_db_path
        self.can_msg = can_msg
        
    def can_msg_print(self):
        C_db = cantools.database.load_file(self.C_db_path)
        print(self.can_msg)
    
if __name__ == '__main__':
    tmp = Can_parser()