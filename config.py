
configParam = {
    # discriminator corner
    'StrAngOn':10.,     # default 15
    'StrAngOff':3.,     # default 5
    'StrAngSpdOn':30.,  # default 50
    'StrAngSpdOff':15., # default 20
    'StrPatience':0.5,  # sec
    
    # # input range
    'StrMin':-420.,  # deg
    'StrMax':+420.,  # deg
    
    'VxMin':+10.,  # kph
    'VxMax':+165.,  # kph
    
    'TimeMin':0., # sec
    'TimeMax':+5., # sec
    'TimeStep':1e-2,    # 0.01 sec
    
    'AyMin':-1.0,   #g
    'AyMax':+1.0,   #g
}

maxValue = {
    'Beta':2.,   #deg
    'YawRate':10., #deg/s
    'Roll':5.,   #deg
    'RollRate':15., #deg/s
}

import numpy as np
CONVERSION_FACTOR = {}
CONVERSION_FACTOR['KPH2MPS'] = 1 / 3.6
CONVERSION_FACTOR['RAD2DEG'] = 180 / np.pi
CONVERSION_FACTOR['DEG2RAD'] = np.pi / 180
CONVERSION_FACTOR['G2MPS2'] = 9.8665

available_vehicles = {
    'IONIQ19':0, 
    'NE':1,
}
available_communications = {
    'UART':0,
    'TCP/IP':1,
}

com_port = {
    0:'/dev/ttyS0',
    1:8888,
}

can_msg_list = {
    0:
        [
        'HEV_PC4', 
        'SAS11', 
        'ESP12'
        ],
    1:
        [
        'CLU_01_20ms',
        'SAS_01_10ms',
        'IMU_01_10ms',
        ],
}

signal_veh_spd = {
    0:'CR_Ems_VehSpd_Kmh',
    1:'CLU_DisSpdValKPH',
}
signal_steer_ang = {
    0:'SAS_Angle',
    1:'SAS_AnglVal',
}
signal_steer_spd = {
    0:'SAS_Speed',
    1:'SAS_SpdVal',
}
signal_ay = {
    0:'LAT_ACCEL',
    1:'IMU_LatAccelVal',
}

StrGearRatio = {
    0:14.7,
    1:15.004,
    # 2:13.,  #JW
}

import os
can_db_path = {
    0:os.path.join(os.path.dirname(__file__), 'dbc', 'C_CAN.dbc'),
    1:os.path.join(os.path.dirname(__file__), 'dbc', 'NE1_2021_FD_C_231212_KMU.dbc'),
}