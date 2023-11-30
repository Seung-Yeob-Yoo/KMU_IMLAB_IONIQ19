import numpy as np
import cv2
import sys
import os
import socket
from config import CONVERSION_FACTOR

class Visualize:
    def __init__(self, background_w, background_h):#, flag_info, roll_out_info, lateral_out_info):
        # flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
        # self.flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
        
        # roll_out_mem = shared_memory.SharedMemory(name=roll_out_info['name'])
        # self.roll_out = np.ndarray(roll_out_info['shape'], dtype=roll_out_info['dtype'], buffer=roll_out_mem.buf)
        
        # lateral_out_mem = shared_memory.SharedMemory(name=lateral_out_info['name'])
        # self.lateral_out = np.ndarray(lateral_out_info['shape'], dtype=lateral_out_info['dtype'], buffer=lateral_out_mem.buf)
        
        # option for background
        self.font = cv2.FONT_HERSHEY_COMPLEX
        self.background_w = background_w
        background_h = background_h
        
        self.line_thickness = 2
        self.font_size = 700/(self.background_w*background_h)**0.5
        
        zero = '0'
        zero_textsize = cv2.getTextSize(zero, self.font, self.font_size, self.line_thickness)[0]
        
        # option for beta
        self.beta_text_color = (0,255,0)
        beta_line_color = (0,255,0)
        beta_rect_color = (0,255,0)
        beta_rect_h = background_h*0.05/2
        beta_line_h = background_h*0.05/2
        beta_rect_upperleft = (10, int(background_h/8-beta_rect_h))
        self.beta_rect_lowerright = (self.background_w-10, int(background_h/8+beta_rect_h))
        beta_text = 'Beta'
        self.beta_textsize = cv2.getTextSize(beta_text, self.font, self.font_size, self.line_thickness)[0]
        
        # option for yaw rate
        self.yaw_rate_text_color = (0,255,0)
        yaw_rate_line_color = (0,255,0)
        yaw_rate_rect_color = (0,255,0)
        self.yaw_rate_rect_h = background_h*0.05/2
        yaw_rate_line_h = background_h*0.05/2
        yaw_rate_rect_upperleft = (10, int(background_h/8*3-self.yaw_rate_rect_h))
        yaw_rate_rect_lowerright = (self.background_w-10, int(background_h/8*3+self.yaw_rate_rect_h))
        yaw_rate_text = 'Yaw rate'
        self.yaw_rate_textsize = cv2.getTextSize(yaw_rate_text, self.font, self.font_size, self.line_thickness)[0]
        
        # option for roll
        self.roll_text_color = (0,255,0)
        roll_line_color = (0,255,0)
        roll_rect_color = (0,255,0)
        self.roll_rect_h = background_h*0.05/2
        roll_line_h = background_h*0.05/2
        roll_rect_upperleft = (10, int(background_h/8*5-self.roll_rect_h))
        roll_rect_lowerright = (self.background_w-10, int(background_h/8*5+self.roll_rect_h))
        roll_text = 'Roll'
        self.roll_textsize = cv2.getTextSize(roll_text, self.font, self.font_size, self.line_thickness)[0]
        
        # option for roll rate
        self.roll_rate_text_color = (0,255,0)
        roll_rate_line_color = (0,255,0)
        roll_rate_rect_color = (0,255,0)
        self.roll_rate_rect_h = background_h*0.05/2
        roll_rate_line_h = background_h*0.05/2
        roll_rate_rect_upperleft = (10, int((background_h/8*7)-self.roll_rate_rect_h))
        roll_rate_rect_lowerright = (self.background_w-10, int((background_h/8*7)+self.roll_rate_rect_h))
        roll_rate_text = 'Roll rate'
        self.roll_rate_textsize = cv2.getTextSize(roll_rate_text, self.font, self.font_size, self.line_thickness)[0]
        
        # fill zeros for background array
        img = np.full((background_h, self.background_w, 3), 0, np.uint8)
        
        # draw beta
        img = cv2.rectangle(img, beta_rect_upperleft, self.beta_rect_lowerright, beta_rect_color, thickness=self.line_thickness)
        img = cv2.putText(img, 'Beta', (int(self.background_w-self.beta_textsize[0])//2, int(self.beta_rect_lowerright[1]+self.beta_textsize[1]*2)), self.font, self.font_size, self.beta_text_color, thickness=self.line_thickness)
        img = cv2.putText(img, zero, (int(self.background_w-zero_textsize[0])//2, int(beta_rect_upperleft[1]-zero_textsize[1]*1.5)), self.font, self.font_size, self.beta_text_color, thickness=self.line_thickness)
        img = cv2.line(img, (int(self.background_w-self.line_thickness)//2, int(beta_rect_upperleft[1]-beta_line_h)), (int(self.background_w-self.line_thickness)//2, int(self.beta_rect_lowerright[1]+beta_line_h)), beta_line_color, thickness=self.line_thickness)
        
        # draw yaw rate
        img = cv2.rectangle(img, yaw_rate_rect_upperleft, yaw_rate_rect_lowerright, yaw_rate_rect_color, thickness=self.line_thickness)
        img = cv2.putText(img, 'Yaw rate', (int(self.background_w-self.yaw_rate_textsize[0])//2, int(yaw_rate_rect_lowerright[1]+self.yaw_rate_textsize[1]*2)), self.font, self.font_size, self.yaw_rate_text_color, thickness=self.line_thickness)
        img = cv2.putText(img, zero, (int(self.background_w-zero_textsize[0])//2, int(yaw_rate_rect_upperleft[1]-zero_textsize[1]*1.5)), self.font, self.font_size, self.yaw_rate_text_color, thickness=self.line_thickness)
        img = cv2.line(img, (int(self.background_w-self.line_thickness)//2, int(yaw_rate_rect_upperleft[1]-yaw_rate_line_h)), (int(self.background_w-self.line_thickness)//2, int(yaw_rate_rect_lowerright[1]+yaw_rate_line_h)), yaw_rate_line_color, thickness=self.line_thickness)
        
        # draw roll
        img = cv2.rectangle(img, roll_rect_upperleft, roll_rect_lowerright, roll_rect_color, thickness=self.line_thickness)
        img = cv2.putText(img, 'Roll', (int(self.background_w-self.roll_textsize[0])//2, int(roll_rect_lowerright[1]+self.roll_textsize[1]*2)), self.font, self.font_size, self.roll_text_color, thickness=self.line_thickness)
        img = cv2.putText(img, zero, (int(self.background_w-zero_textsize[0])//2, int(roll_rect_upperleft[1]-zero_textsize[1]*1.5)), self.font, self.font_size, self.roll_text_color, thickness=self.line_thickness)
        img = cv2.line(img, (int(self.background_w-self.line_thickness)//2, int(roll_rect_upperleft[1]-roll_line_h)), (int(self.background_w-self.line_thickness)//2, int(roll_rect_lowerright[1]+roll_line_h)), roll_line_color, thickness=self.line_thickness)
        
        #draw roll rate
        img = cv2.rectangle(img, roll_rate_rect_upperleft, roll_rate_rect_lowerright, roll_rate_rect_color, thickness=self.line_thickness)
        img = cv2.putText(img, 'Roll rate', (int(self.background_w-self.roll_rate_textsize[0])//2, int(roll_rate_rect_lowerright[1]+self.roll_rate_textsize[1]*2)), self.font, self.font_size, self.roll_rate_text_color, thickness=self.line_thickness)
        img = cv2.putText(img, zero, (int(self.background_w-zero_textsize[0])//2, int(roll_rate_rect_upperleft[1]-zero_textsize[1]*1.5)), self.font, self.font_size, self.roll_rate_text_color, thickness=self.line_thickness)
        img = cv2.line(img, (int(self.background_w-self.line_thickness)//2, int(roll_rate_rect_upperleft[1]-roll_rate_line_h)), (int(self.background_w-self.line_thickness)//2, int(roll_rate_rect_lowerright[1]+roll_rate_line_h)), roll_rate_line_color, thickness=self.line_thickness)
        
        self.canvas = np.array(img, dtype=np.uint8)
        
    def visualize(self): #(self, flag_info, roll_out_info, lateral_out_info, stop_event):
        font_size = 0.7
        
        host = 'localhost'
        port = 9999
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((host, port))
        sock.listen(1)
        conn, addr = sock.accept()
        
        while True:
            recv = conn.recv(1024).decode().split(',')
            print(recv)
            continue
            flag = np.bool_(recv[0])
            roll_out = np.array([recv[1], recv[2]], dtype=np.float32)
            lateral_out = np.array([recv[3], recv[4]], dtype=np.float32)
            
            if flag:
                roll_a = roll_out[0, 0] * CONVERSION_FACTOR['RAD2DEG']
                roll_r = roll_out[0, 1]
                beta_a = lateral_out[0, 0]* CONVERSION_FACTOR['RAD2DEG']
                yaw_r = lateral_out[0, 1]
                
                img = cv2.rectangle(self.canvas, (int(self.background_w-self.line_thickness)//2, (int(background_h/8-beta_rect_h))), (int(self.background_w-self.line_thickness)//2+(beta_a), int(background_h/8+beta_rect_h)), (0,0,255), -1)
                img = cv2.putText(img, '0.0', (int(self.background_w+self.beta_textsize[0]+(self.background_w/40))//2, int(self.beta_rect_lowerright[1]+self.beta_textsize[1]*2)), self.font, font_size, self.beta_text_color, thickness=self.line_thickness)
                
                img = cv2.rectangle(img, (int(self.background_w-self.line_thickness)//2, (int(background_h/8*3-beta_rect_h))), (int(self.background_w-self.line_thickness)//2-(100), int(background_h/8*3+beta_rect_h)), (0,0,255), -1)
                img = cv2.putText(img, '0.0', (int(self.background_w+self.yaw_rate_textsize[0]+(self.background_w/40))//2, int(self.beta_rect_lowerright[1]+self.yaw_rate_textsize[1]*2)), self.font, font_size, self.beta_text_color, thickness=self.line_thickness)
                
                img = cv2.rectangle(img, (int(self.background_w-self.line_thickness)//2, (int(background_h/8*5-beta_rect_h))), (int(self.background_w-self.line_thickness)//2+(roll_a), int(background_h/8*5+beta_rect_h)), (0,0,255), -1)
                img = cv2.putText(img, '0.0', (int(self.background_w+self.roll_textsize[0]+(self.background_w/40))//2, int(self.beta_rect_lowerright[1]+self.roll_textsize[1]*2)), self.font, font_size, self.beta_text_color, thickness=self.line_thickness)
                
                img = cv2.rectangle(img, (int(self.background_w-self.line_thickness)//2, (int(background_h/8*7-beta_rect_h))), (int(self.background_w-self.line_thickness)//2-(100), int(background_h/8*7+beta_rect_h)), (0,0,255), -1)
                img = cv2.putText(img, '0.0', (int(self.background_w+self.roll_rate_textsize[0]+(self.background_w/40))//2, int(self.beta_rect_lowerright[1]+self.roll_rate_textsize[1]*2)), self.font, font_size, self.beta_text_color, thickness=self.line_thickness)
                
                cv2.imshow('', img)
            cv2.imshow('', self.canvas)
        sock.close()
        cv2.destroyAllWindows()
        print('[I] Visualization is ended')

if __name__ == '__main__':
    background_w = 700
    background_h = 700
    
    beta_rect_h = background_h*0.05/2
    
    img = Visualize(background_w, background_h).visualize() # .visualize(flag_info, roll_out_info, lateral_out_info, stop_event)

    # img = cv2.rectangle(img, (int(background_w)//2, (int(background_h/8-beta_rect_h))), (background_w-10, int(background_h/8+beta_rect_h)), (0,0,255), -1)
    # img = cv2.rectangle(img, (int(background_w)//2, (int(background_h/8-beta_rect_h))), (10, int(background_h/8+beta_rect_h)), (0,0,255), -1)
    
    # cv2.imshow('', img)
    # cv2.waitKey(0)
