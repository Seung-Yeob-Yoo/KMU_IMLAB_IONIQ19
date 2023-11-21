from config import configParam
from can_parser import CAN_parser
from time import time

class DiscriminatorCornerDuration(object):
    def __init__(self, vehicle='IONIQ19'):
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
        self.can_msg_list = ['HEV_PC4', 'SAS11', 'ESP12'], # KMU
        self.signal_veh_spd = 'CR_Ems_VehSpd_Kmh'
        self.signal_steer_ang = 'SAS_Angle'
        self.signal_steer_spd = 'SAS_Speed'
        self.signal_ay = 'LAT_ACCEL'
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
            print(">>>>> Out of range (Steer Angle):", steer_ang)
            
        if veh_spd < self.minVehSpd_kph or veh_spd > self.maxVehSpd_kph:
            flag = False
            print(">>>>> Out of range (Velocity):", veh_spd)
        
        if ay < self.minAy_g or ay > self.maxAy_g:
            flag = False
            print(">>>>> Out of range (Lateral Acceleration):", ay)
            
        return flag

    def discriminate(self):
        flag_driving = False
        flag_corner = False
        
        steer_ang = self.latest_signal_dic.pop(self.signal_steer_ang)
        steer_spd = self.latest_signal_dic.pop(self.signal_steer_spd)
        veh_spd = self.latest_signal_dic.pop(self.signal_veh_spd)
        ay = self.latest_signal_dic.pop(self.signal_ay)
        
        # get corner flag
        flag_corner = self.get_corner_flag(steer_ang, steer_spd)
        # get driving flag
        flag_driving = self.get_driving_flag(steer_ang, veh_spd, ay)
            
        if flag_corner & flag_driving:
            if self.flag:
                self.time_from_init += self.sampling_time
            
            else:
                self.time_from_init = 0.
                self.flag = True
                self.cnt_patience = 0
        
        else:
            if self.cnt_patience <= self.max_cnt_patience:
                self.time_from_init += self.sampling_time
                self.cnt_patience += 1
                
            else:
                self.cnt_patience = 0
                self.flag = False
                self.time_from_init = -1
        
        return self.time_from_init
    
    def run(self):
        
        for data_dic, data_time in self.can_parser.get_can_data(self.can_signal_list):
            # print(time() - data_time)
            for k, v in data_dic.items():
                self.latest_signal_dic.update({k, v})
            
            if len(self.latest_signal_dic.keys()) < len(self.can_signal_list):
                continue
            
            if (time() - prev_time) < self.sampling_time:
                continue
            
            if (time() - prev_time) > self.sampling_time*1.5:
                raise TimeoutError(f"Operation timed out, {time()-prev_time}")
            
            corner_duration_time = self.discriminate()
            prev_time = time()
            yield corner_duration_time
            
        
        
if __name__ == "__main__":
    discriminator = DiscriminatorCornerDuration()
    for duration_time in discriminator.run():
        print(duration_time)