from config import configParam, can_msg_list, signal_ay, signal_steer_ang, signal_steer_spd
from can_parser import CAN_parser

class DiscriminatorCorner(object):
    def __init__(self, vehicle_id=0):
        # Criteria for Corner
        self.steerAngleOn = configParam['StrAngOn']
        self.steerAngleOff =configParam['StrAngOff']
        self.steerAngleSpeedOn = configParam['StrAngSpdOn']
        self.steerAngleSpeedOff = configParam['StrAngSpdOff']
        self.patience_sec = configParam['StrPatience']
        
        # Criteria for Driving
        self.minStrAng_deg = configParam['StrMin']
        self.maxStrAng_deg = configParam['StrMax']
        
        self.minVehSpd_kph = configParam['VxMin']
        self.maxVehSpd_kph = configParam['VxMax']
        
        self.minAy_g = configParam['AyMin']
        self.maxAy_g = configParam['AyMax']
        
        # Criteria for Temporal information
        self.maxTime_sec = configParam['TimeMax']
        self.sampling_time = configParam['TimeStep']
        
        # Results variables for discrimination
        self.flag = False
        self.time_from_init = -1.
        self.cnt_patience = 0
        self.max_cnt_patience = int(self.patience_sec / self.sampling_time)
        
        self.check_info()
        
        # Set CAN Parser
        self.can_msg_list = can_msg_list[vehicle_id] # KMU
        self.signal_veh_spd = signal_steer_ang[vehicle_id]
        self.signal_steer_ang = signal_steer_spd[vehicle_id]
        self.signal_steer_spd = signal_steer_spd[vehicle_id]
        self.signal_ay = signal_ay[vehicle_id]
        
        self.can_signal_list = [self.signal_veh_spd, self.signal_steer_ang, self.signal_steer_spd, self.signal_ay]
        
        self.can_parser = CAN_parser(
                vehicle=vehicle,
                can_msg_list = self.can_msg_list,
                )
        self.latest_signal_dic = {}
        
    def check_info(self):
        print("Criteria for Corner Discrimination:")
        print("\t Steering Angle Transient: {}~{} [deg]".format(self.steerAngleOff, self.steerAngleOn))
        print("\t Steering Angle Speed Transient: {}~{} [deg/s]" .format(self.steerAngleSpeedOff, self.steerAngleSpeedOn))
        print("\t Maximum count for patience: {}" .format(self.max_cnt_patience))
        print('')
        print("Criteria for Driving Discrimination:")
        print("\t Steering Angle: {}~{} [deg]".format(self.minStrAng_deg, self.maxStrAng_deg))
        print("\t Vehicle Velocity: {}~{} [kph]".format(self.minVehSpd_kph, self.maxVehSpd_kph))

    def get_corner_flag(self, steer_ang, steer_spd):
        flag_corner = False
        
        norm_steer_ang = (abs(steer_ang) - self.steerAngleOff) / (self.steerAngleOn - self.steerAngleOff)
        norm_steer_spd = (abs(steer_spd) - self.steerAngleSpeedOff) / (self.steerAngleSpeedOn - self.steerAngleSpeedOff)
            
        if norm_steer_ang + norm_steer_spd > 1.0:
            flag_corner = True

        return flag_corner
    
    def get_driving_flag(self, steer_ang, veh_spd, ay):
        flag = True
        if steer_ang < self.minStrAng_deg or steer_ang > self.maxStrAng_deg:
            flag = False
            print(f">>>>> Out of range (Steer Angle): {steer_ang:.2f}")
            
        if veh_spd < self.minVehSpd_kph or veh_spd > self.maxVehSpd_kph:
            flag = False
            print(f">>>>> Out of range (Velocity): {veh_spd:.2f}")
        
        if ay < self.minAy_g or ay > self.maxAy_g:
            flag = False
            print(f">>>>> Out of range (Lateral Acceleration: {ay:.2f})")
            
        return flag

    def discriminate(self):
        flag_driving = False
        flag_corner = False
        
        steer_ang = self.latest_signal_dic.get(self.signal_steer_ang)
        steer_spd = self.latest_signal_dic.get(self.signal_steer_spd)
        veh_spd = self.latest_signal_dic.get(self.signal_veh_spd)
        ay = self.latest_signal_dic.get(self.signal_ay) / 9.81
        
        # get corner flag
        flag_corner = self.get_corner_flag(steer_ang, steer_spd)
        # get driving flag
        flag_driving = self.get_driving_flag(steer_ang, veh_spd, ay)
            
        if flag_corner and flag_driving:
            if not self.flag:
                self.flag = True
                self.cnt_patience = 0
        
        else:
            if self.flag:
                if self.cnt_patience <= self.max_cnt_patience:
                    self.cnt_patience += 1
                else:
                    self.cnt_patience = 0
                    self.flag = False
        
    
    def run(self):
        for data_dic, data_time in self.can_parser.get_can_data(self.can_signal_list):
            for k, v in data_dic.items():
                self.latest_signal_dic.update({k:v})
            
            if len(self.latest_signal_dic.keys()) < len(self.can_signal_list):
                continue
            
            self.discriminate()

            
            yield self.flag
            

from multiprocessing import shared_memory
import numpy as np
def run_discriminator(vehicle_id, flag_info, stop_event):
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)

    discriminator = DiscriminatorCorner(vehicle_id=vehicle_id)
    
    for corner_flag in discriminator.run():
        if stop_event.is_set():
            break
        flag[0] = corner_flag
    
    flag_mem.close()
        
if __name__ == "__main__":
    discriminator = DiscriminatorCorner()
    for duration_time in discriminator.run():
        print(f"{duration_time}       ", end='\r')
