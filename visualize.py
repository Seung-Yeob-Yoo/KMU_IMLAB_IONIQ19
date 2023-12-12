import numpy as np
import cv2
import sys
import os
import socket
import time
import serial
import argparse
from config import CONVERSION_FACTOR, maxValue

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
parser = argparse.ArgumentParser(description='Inference environment setup')
parser.add_argument('--port', '-p', type=str, default="/dev/ttyTHS1", help='port name for serial communication [RX]')
args = parser.parse_args()

class Visualize: 
    def __init__(self, signal_list=['Beta', 'YawRate', 'Roll', 'RollRate'], w=1000, h=1000):
        # option for drawing
        self.delay_time = 0.05
        
        self.maxValue = maxValue
        
        # option for background
        ## canvas
        self.w = w
        self.h = h
        
        ## font
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.font_size = 1.5
        self.value_size = self.font_size * 1.
        
        # thickness
        self.thick = 2
        
        # option for color
        self.base_color = (0, 255, 0)
        self.gauge_color = (0, 0, 255)
        
        # option for signal
        self.signal_list = signal_list
        self.num_signal = len(signal_list)
        
        # option for rect
        self.w_offset = 10
        self.h_offset = int((self.h / self.num_signal) // 3)
        self.font_offset = 15
        self.line_offset = 8
        self.value_offset = 120
        
        self.canvas = self.get_background()
        
    def get_background(self):
        # fill zeros for background array
        img = np.full((self.h, self.w, 3), 0, np.uint8)
        
        for i, signal_name in enumerate(self.signal_list):
            img = self.draw_bar(img, i, signal_name, self.base_color)
        
        return np.array(img, dtype=np.uint8)
            
    def get_font_size(self, font_face):
        font_size, _ = cv2.getTextSize(
                        text=font_face, 
                        fontFace=self.font, 
                        fontScale=self.font_size, 
                        thickness=self.thick,)
        return font_size
        
    def draw_bar(self, img, i, name, color):
        top = int((i*(self.h / self.num_signal)) + self.h_offset)
        left = int(self.w_offset)
        bottom = int(((i+1)*(self.h / self.num_signal)) - self.h_offset)
        right = int(self.w - self.w_offset)
        
        self.w_box = int(right - left)
        self.h_box = int(bottom - top)
        
        img = cv2.rectangle(img, (left, top), (right, bottom), 
                            color=color, 
                            thickness=self.thick)
        
        center = int(self.w // 2)
        top_line = int(top - self.line_offset)
        bottom_line = int(bottom + self.line_offset)
        img = cv2.line(img, 
                    (center, top_line), (center, bottom_line),
                    color=color,
                    thickness=self.thick,
                    )
        
        # signal name
        ## get fontsize
        font_size = self.get_font_size(name)
        self.h_font = font_size[1]
        ## get font position
        font_position = (int((self.w - font_size[0])//2), int(bottom + (font_size[1] + self.font_offset)))
        img = cv2.putText(img, 
                        name, 
                        font_position,
                        fontFace=self.font, 
                        fontScale=self.font_size, 
                        color=color, 
                        thickness=self.thick,
                        )
        
        # zero
        ## get fontsize
        font_size = self.get_font_size('0')
        ## get font position
        font_position = (int((self.w//2 - font_size[0]//2)+1), int(top - self.font_offset))
        img = cv2.putText(img, 
                        '0',
                        font_position,
                        fontFace=self.font, 
                        fontScale=self.font_size, 
                        color=color, 
                        thickness=self.thick,
                        )
        
        return img
                
                
    def draw_gauge(self, img, i, name, value, color):
        top = int((i*(self.h / self.num_signal)) + self.h_offset)
        bottom = int(((i+1)*(self.h / self.num_signal)) - self.h_offset)
        
        max_value = self.maxValue[name]
        cur_w = int((self.w_box * value) / max_value)
        
        left = min(int(self.w//2 + cur_w), int(self.w//2))
        right = max(int(self.w//2 + cur_w), int(self.w//2))
        
        img = cv2.rectangle(img, 
                            (left, top),
                            (right, bottom),
                            color=color,
                            thickness=-1,
                            )
        
        bottom_value = int(bottom + (self.h_font + self.font_offset))
        left_value = int(self.w//2) + self.value_offset
        
        img = cv2.putText(img, 
                        f"{value:.1f}", 
                        (left_value, bottom_value),
                        fontFace=self.font, 
                        fontScale=self.value_size, 
                        color=color, 
                        thickness=self.thick,
                        )
        
        return img
                    
    
    def visualize(self, test=False, uart=False): 
        if not test:
            if uart:
                # Jetson nano 수신부
                jet_rx = serial.Serial(
                    port=args.port,
                    baudrate=115200,
                    bytesize=serial.EIGHTBITS,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                )
            else:
                # set TCP/IP communication
                host = 'localhost'
                port = 8888
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((host, port))
                sock.listen(1)
                conn, addr = sock.accept()

        while True:
            img = self.get_background()
            if not test:
                if uart:
                    #Receive data
                    data_size= 16
                    received_data = jet_rx.read(data_size) 
                    recv = np.frombuffer(received_data, dtype=np.float32).reshape(4)
                else:
                    # get communication
                    recv = conn.recv(1024).decode().split(',')
                    if (recv[0] != 'str') or (recv[-2] != 'end'):
                        continue
                
            else:
                random_values = [np.random.random()*0.1 for x in range(self.num_signal)]
                recv = ['str', 'True'] + random_values

            # flag = (recv[1])
            values = {
            'Roll':np.float32(recv[2]) * CONVERSION_FACTOR['RAD2DEG'],
            'RollRate':np.float32(recv[3]) * CONVERSION_FACTOR['RAD2DEG'],
            'Beta':np.float32(recv[4]) * CONVERSION_FACTOR['RAD2DEG'],
            'YawRate':np.float32(recv[5]) * CONVERSION_FACTOR['RAD2DEG'],
            }
            
            for i, signal_name in enumerate(self.signal_list):
                value = values[signal_name]
                img = self.draw_gauge(img, i, signal_name, value, self.gauge_color)
                
            cv2.imshow('', img)
            if cv2.waitKey(1)&0xFF == 13: # 13 is the ASCII code for Enter key
                if not test:
                    sock.close()
                break
            
            time.sleep(self.delay_time)
        sock.close()
        cv2.destroyAllWindows()
        print('[I] Visualization is ended')

if __name__ == '__main__':
    visualizer = Visualize()
    visualizer.visualize(test=False)
