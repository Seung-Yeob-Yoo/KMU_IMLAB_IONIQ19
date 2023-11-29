import numpy as np
import cv2
import sys

def get_background(background_w, background_h):
    # option for background
    font = cv2.FONT_HERSHEY_COMPLEX
    background_w = background_w
    backgroud_h = background_h
    
    line_thickness = 2
    font_size = 700/(background_w*background_h)**0.5
    
    zero = '0'
    zero_textsize = cv2.getTextSize(zero, font, font_size, line_thickness)[0]
    
    # option for beta
    beta_text_color = (0,255,0)
    beta_line_color = (0,255,0)
    beta_rect_color = (0,255,0)
    beta_rect_h = backgroud_h*0.05/2
    beta_line_h = backgroud_h*0.05/2
    beta_rect_upperleft = (10, int(backgroud_h/8-beta_rect_h))
    beta_rect_lowerright = (background_w-10, int(backgroud_h/8+beta_rect_h))
    beta_text = 'Beta'
    beta_textsize = cv2.getTextSize(beta_text, font, font_size, line_thickness)[0]
    
    # option for yaw rate
    yaw_rate_text_color = (0,255,0)
    yaw_rate_line_color = (0,255,0)
    yaw_rate_rect_color = (0,255,0)
    yaw_rate_rect_h = backgroud_h*0.05/2
    yaw_rate_line_h = backgroud_h*0.05/2
    yaw_rate_rect_upperleft = (10, int(backgroud_h/8*3-yaw_rate_rect_h))
    yaw_rate_rect_lowerright = (background_w-10, int(backgroud_h/8*3+yaw_rate_rect_h))
    yaw_rate_text = 'Yaw rate'
    yaw_rate_textsize = cv2.getTextSize(yaw_rate_text, font, font_size, line_thickness)[0]
    
    # option for roll
    roll_text_color = (0,255,0)
    roll_line_color = (0,255,0)
    roll_rect_color = (0,255,0)
    roll_rect_h = backgroud_h*0.05/2
    roll_line_h = backgroud_h*0.05/2
    roll_rect_upperleft = (10, int(backgroud_h/8*5-roll_rect_h))
    roll_rect_lowerright = (background_w-10, int(backgroud_h/8*5+roll_rect_h))
    roll_text = 'Roll'
    roll_textsize = cv2.getTextSize(roll_text, font, font_size, line_thickness)[0]
    
    # option for roll rate
    roll_rate_text_color = (0,255,0)
    roll_rate_line_color = (0,255,0)
    roll_rate_rect_color = (0,255,0)
    roll_rate_rect_h = backgroud_h*0.05/2
    roll_rate_line_h = backgroud_h*0.05/2
    roll_rate_rect_upperleft = (10, int((backgroud_h/8*7)-roll_rate_rect_h))
    roll_rate_rect_lowerright = (background_w-10, int((backgroud_h/8*7)+roll_rate_rect_h))
    roll_rate_text = 'Roll rate'
    roll_rate_textsize = cv2.getTextSize(roll_rate_text, font, font_size, line_thickness)[0]
    
    # fill zeros for background array
    img = np.full((backgroud_h, background_w, 3), 0, np.uint8)
    
    # draw beta
    img = cv2.rectangle(img, beta_rect_upperleft, beta_rect_lowerright, beta_rect_color, thickness=line_thickness)
    img = cv2.putText(img, 'Beta', (int(background_w-beta_textsize[0])//2, int(beta_rect_lowerright[1]+beta_textsize[1]*2)), font, font_size, beta_text_color, thickness=line_thickness)
    img = cv2.putText(img, '0', (int(background_w-zero_textsize[0])//2, int(beta_rect_upperleft[1]-zero_textsize[1]*1.5)), font, font_size, beta_text_color, thickness=line_thickness)
    img = cv2.line(img, (int(background_w-line_thickness)//2, int(beta_rect_upperleft[1]-beta_line_h)), (int(background_w-line_thickness)//2, int(beta_rect_lowerright[1]+beta_line_h)), beta_line_color, thickness=line_thickness)
    
    # draw yaw rate
    img = cv2.rectangle(img, yaw_rate_rect_upperleft, yaw_rate_rect_lowerright, yaw_rate_rect_color, thickness=line_thickness)
    img = cv2.putText(img, 'Yaw rate', (int(background_w-yaw_rate_textsize[0])//2, int(yaw_rate_rect_lowerright[1]+yaw_rate_textsize[1]*2)), font, font_size, yaw_rate_text_color, thickness=line_thickness)
    img = cv2.putText(img, '0', (int(background_w-zero_textsize[0])//2, int(yaw_rate_rect_upperleft[1]-zero_textsize[1]*1.5)), font, font_size, yaw_rate_text_color, thickness=line_thickness)
    img = cv2.line(img, (int(background_w-line_thickness)//2, int(yaw_rate_rect_upperleft[1]-yaw_rate_line_h)), (int(background_w-line_thickness)//2, int(yaw_rate_rect_lowerright[1]+yaw_rate_line_h)), yaw_rate_line_color, thickness=line_thickness)
    
    # draw roll
    img = cv2.rectangle(img, roll_rect_upperleft, roll_rect_lowerright, roll_rect_color, thickness=line_thickness)
    img = cv2.putText(img, 'Roll', (int(background_w-roll_textsize[0])//2, int(roll_rect_lowerright[1]+roll_textsize[1]*2)), font, font_size, roll_text_color, thickness=line_thickness)
    img = cv2.putText(img, '0', (int(background_w-zero_textsize[0])//2, int(roll_rect_upperleft[1]-zero_textsize[1]*1.5)), font, font_size, roll_text_color, thickness=line_thickness)
    img = cv2.line(img, (int(background_w-line_thickness)//2, int(roll_rect_upperleft[1]-roll_line_h)), (int(background_w-line_thickness)//2, int(roll_rect_lowerright[1]+roll_line_h)), roll_line_color, thickness=line_thickness)
    
    #draw roll rate
    img = cv2.rectangle(img, roll_rate_rect_upperleft, roll_rate_rect_lowerright, roll_rate_rect_color, thickness=line_thickness)
    img = cv2.putText(img, 'Roll rate', (int(background_w-roll_rate_textsize[0])//2, int(roll_rate_rect_lowerright[1]+roll_rate_textsize[1]*2)), font, font_size, roll_rate_text_color, thickness=line_thickness)
    img = cv2.putText(img, '0', (int(background_w-zero_textsize[0])//2, int(roll_rate_rect_upperleft[1]-zero_textsize[1]*1.5)), font, font_size, roll_rate_text_color, thickness=line_thickness)
    img = cv2.line(img, (int(background_w-line_thickness)//2, int(roll_rate_rect_upperleft[1]-roll_rate_line_h)), (int(background_w-line_thickness)//2, int(roll_rate_rect_lowerright[1]+roll_rate_line_h)), roll_rate_line_color, thickness=line_thickness)
    
    return np.array(img, dtype=np.uint8)

from multiprocessing import shared_memory
def visualize(flag_info, roll_out_info, lateral_out_info, stop_event):
    background_w = 700
    background_h = 700
    
    img = get_background(background_w, background_h)
    
    flag_mem = shared_memory.SharedMemory(name=flag_info['name'])
    flag = np.ndarray(flag_info['shape'], dtype=flag_info['dtype'], buffer=flag_mem.buf)
    
    roll_out_mem = shared_memory.SharedMemory(name=roll_out_info['name'])
    roll_out = np.ndarray(roll_out_info['shape'], dtype=roll_out_info['dtype'], buffer=roll_out_mem.buf)
    
    lateral_out_mem = shared_memory.SharedMemory(name=lateral_out_info['name'])
    lateral_out = np.ndarray(lateral_out_info['shape'], dtype=lateral_out_info['dtype'], buffer=lateral_out_mem.buf)
    
    while True:
        if stop_event.is_set():
            break
        
        if flag:
            roll_a = roll_out[0, 0]
            roll_r = roll_out[0, 1]
            beta_a = lateral_out[0, 0]
            yaw_r = lateral_out[0, 1]
            
            print(roll_a, roll_r, beta_a, yaw_r)
            
            flag_img = cv2.rectangle(img, )
            cv2.imshow('', flag_img)
            
        cv2.imshow('', img)
            
    cv2.destroyAllWindows()
    print('[I] Visualization is ended')
    
if __name__ == '__main__':
    background_w = 700
    background_h = 700
    
    img = get_background(background_w, background_h)
    cv2.imshow('', img)
    cv2.waitKey(0)