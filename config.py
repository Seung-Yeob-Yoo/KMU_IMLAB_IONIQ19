
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

vehicleParam = {
    'NE':{
    'StrGearRatio' : 15.004,  # steering wheel angle to front wheel angle
    },
    'JW':{
    'StrGearRatio' : 13.,  # steering wheel angle to front wheel angle
    },
    'IONIQ19':{
    'StrGearRatio' : 14.7,  # steering wheel angle to front wheel angle
    },
}

import numpy as np
CONVERSION_FACTOR = {}
CONVERSION_FACTOR['KPH2MPS'] = 1 / 3.6
CONVERSION_FACTOR['RAD2DEG'] = 180 / np.pi
CONVERSION_FACTOR['DEG2RAD'] = np.pi / 180
CONVERSION_FACTOR['G2MPS2'] = 9.8665
