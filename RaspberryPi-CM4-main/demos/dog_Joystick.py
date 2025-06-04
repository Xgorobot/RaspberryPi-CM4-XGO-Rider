#!/usr/bin/env python3
# coding=utf-8

import os, struct, sys
from xgolib import XGO
import time
import threading
from uiutils import (
    lcd_draw_string, display, splash, draw,language,
    font2, Button,get_font
)
from PIL import Image, ImageDraw,ImageFont
font1=get_font(16)
button=Button()
splash_theme_color = (15, 21, 46)
la=language()
lianjie_image = Image.open("/home/pi/RaspberryPi-CM4-main/pics/lianjie@2x.png") 
weilianjie_image = Image.open("/home/pi/RaspberryPi-CM4-main/pics/weilianjie@2x.png")

dog = XGO("xgorider")

def clear_bottom():
    draw.rectangle([(0, 111), (320, 240)], fill=splash_theme_color)

def clear_top():
    draw.rectangle([(0, 0), (320, 120)], fill=splash_theme_color)
    
def show_connection_status(connected):
    clear_top()
    
    if connected:
        img = lianjie_image.convert("RGBA")
    else:
        img = weilianjie_image.convert("RGBA")
    
    splash.paste(img, (25, 0), img)
    display.ShowImage(splash)

class XGO_Joystick(object):

    def __init__(self, dog, js_id=0, debug=False):
        self.__debug = debug
        self.__js_id = int(js_id)
        self.__js_isOpen = False
        self.__dog = dog
        self.__step_control = 70
        self.__pace_freq = 2
        self.__height = 105
        self.__ignore_count = 20

        self.__STEP_SCALE_X = 0.25 
        self.__STEP_SCALE_Y = 0.2
        self.__STEP_SCALE_Z = 0.7
        
        self.STATE_OK = 0
        self.STATE_NO_OPEN = 1
        self.STATE_DISCONNECT = 2
        self.STATE_KEY_BREAK = 3
        
        # Find the joystick device.
        print('Joystick Available devices:')
        # Shows the joystick list of the Controler, for example: /dev/input/js0
        for fn in os.listdir('/dev/input'):
            if fn.startswith('js'):
                print('    /dev/input/%s' % (fn))

        # Open the joystick device.
        try:
            js = '/dev/input/js' + str(self.__js_id)
            self.__jsdev = open(js, 'rb')
            self.__js_isOpen = True
            print('---Opening %s Succeeded---' % js)
            show_connection_status(True)
        except:
            self.__js_isOpen = False
            print('---Failed To Open %s---' % js)
            show_connection_status(False)
            
        # Defining Functional List
        self.__function_names = {
            # BUTTON FUNCTION
            0x0100 : 'A',
            0x0101 : 'B',
            0x0102 : 'X',
            0x0103 : 'Y',
            0x0104 : 'L1',
            0x0105 : 'R1',
            0x0106 : 'SELECT',
            0x0107 : 'START',
            0x0108 : 'MODE',
            0x0109 : 'BTN_RK1',
            0x010A : 'BTN_RK2',

            # AXIS FUNCTION
            0x0200 : 'RK1_LEFT_RIGHT',
            0x0201 : 'RK1_UP_DOWN',
            0x0202 : 'L2',
            0x0203 : 'RK2_LEFT_RIGHT',
            0x0204 : 'RK2_UP_DOWN',
            0x0205 : 'R2',
            0x0206 : 'WSAD_LEFT_RIGHT',
            0x0207 : 'WSAD_UP_DOWN',
        }

    def __del__(self):
        if self.__js_isOpen:
            self.__jsdev.close()
        if self.__debug:
            print("\n---Joystick DEL---\n")

    # Return joystick state
    def is_Opened(self):
        return self.__js_isOpen
    
    # transform data
    def __my_map(self, x, in_min, in_max, out_min, out_max):
        return (out_max - out_min) * (x - in_min) / (in_max - in_min) + out_min

    # reset DOGZILLA
    def __dog_reset(self):
        self.__dog.reset()
        self.__step_control = 70
        self.__pace_freq = 2
        self.__height = 105

    # Control robot
    def __data_processing(self, name, value):
        print(f"Input Event - Name: {name}, Value: {value}")
        if name=="RK1_LEFT_RIGHT":
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__step_control))
            if value == 0:
                self.__dog.rider_turn(0)
            elif value == 1 or value == -1:
                fvalue = int(self.__my_map(self.__step_control, 0, 100, 20, self.__STEP_SCALE_Z*100))*value
                self.__dog.rider_turn(fvalue)
        elif name == 'RK1_UP_DOWN':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__step_control))
            fvalue = int(self.__step_control * self.__STEP_SCALE_X * value)
            self.__dog.rider_move_x(fvalue)
        elif name == 'RK2_UP_DOWN':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            fvalue = (value * self.__step_control * self.__STEP_SCALE_Y)
            self.__dog.rider_move_x(fvalue)
        elif name == 'RK2_LEFT_RIGHT':
            value = value / 32767
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            fvalue = value * 15
            self.__dog.rider_roll(fvalue)
        
        elif name == 'A':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__height = self.__height - 10
                if self.__height < 75:
                    self.__height = 75
                self.__dog.rider_height(self.__height)
        elif name == 'B':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__dog.rider_roll(-15)
            else:
                self.__dog.rider_roll(0)
        elif name == 'X':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__dog.rider_roll(15)
            else:
                self.__dog.rider_roll(0)
        elif name == 'Y':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__height = self.__height + 10
                if self.__height > 115:
                    self.__height = 115
                self.__dog.rider_height(self.__height)
        elif name == 'L1':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__dog.rider_action(1)  
        elif name == 'R1':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                self.__dog.rider_action(2)  
        elif name == 'SELECT':
            if self.__debug:
                print (name, ":", value)
            if value == 1:
                pass  # Removed obstacle crossing mode
        elif name == 'START':
            if self.__debug:
                print (name, ":", value)
            # Stop the action and restore the original position
            if value == 1:
                self.__dog_reset()
        elif name == 'MODE':
            if self.__debug:
                print (name, ":", value)
        elif name == "L2":
            value = ((value/32767)+1)/2
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            if value == 1:
                self.__dog.rider_action(4)  # PRAY
        elif name == "R2":
            value = ((value/32767)+1)/2
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            if value == 1:
                self.__dog.rider_action(5)  # STAND
            
        elif name == 'WSAD_LEFT_RIGHT':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f, %d" % (name, value, self.__step_control))
            if value == 0:
                self.__dog.rider_turn(0)
            elif value == 1 or value == -1:
                fvalue = int(self.__my_map(self.__step_control, 0, 100, 20, self.__STEP_SCALE_Z*100))*value
                self.__dog.rider_turn(fvalue)
        elif name == 'WSAD_UP_DOWN':
            value = -value / 32767
            if self.__debug:
                print ("%s : %.3f" % (name, value))
            fvalue = (value * self.__step_control * self.__STEP_SCALE_Y)
            self.__dog.rider_move_x(fvalue)
        else:
            pass

    # Handles events for joystick
    def joystick_handle(self):
        if not self.__js_isOpen:
            show_connection_status(False)
            return self.STATE_NO_OPEN
        try:
            evbuf = self.__jsdev.read(8)
            if evbuf:
                time, value, type, number = struct.unpack('IhBB', evbuf)
                func = type << 8 | number
                name = self.__function_names.get(func)
                if name != None:
                    self.__data_processing(name, value)
                else:
                    if self.__ignore_count > 0:
                        self.__ignore_count = self.__ignore_count - 1
                    if self.__debug and self.__ignore_count == 0:
                        print("Key Value Invalid")
            return self.STATE_OK
        except KeyboardInterrupt:
            if self.__debug:
                print('Key Break Joystick')
            return self.STATE_KEY_BREAK
        except:
            self.__js_isOpen = False
            print('---Joystick Disconnected---')
            show_connection_status(False)
            return self.STATE_DISCONNECT

    # reconnect Joystick
    def reconnect(self):
        try:
            js = '/dev/input/js' + str(self.__js_id)
            self.__jsdev = open(js, 'rb')
            self.__js_isOpen = True
            self.__ignore_count = 20
            print('---Opening %s Succeeded---' % js)
            show_connection_status(True)
            return True
        except:
            self.__js_isOpen = False
            show_connection_status(False)
            return False
            
def show_controller_help():
    clear_bottom()
    
    if la == 'cn':
        text_lines = [
            ("←→↑↓: 移动控制",30,150),
            ("A/Y: 高度调节", 30,170),
            ("X/B: 左右倾斜", 190,150),
            ("L/R: 动作模式",190,170),
        ]
    else:
        text_lines = [
            ("←→↑↓: Movement",30,150),
            ("A/Y: Height", 30,170), 
            ("X/B: Tilting",190,150),
            ("L/R: Modes", 190,170),
        ]
    
    for text,x,y in text_lines:
        lcd_draw_string(draw, x, y, text, color=(0, 255, 255), scale=font1, mono_space=False)
    
    display.ShowImage(splash)

def button_listener():
    while True:
        if button.press_b():
            print("Button B pressed, exiting...")
            os._exit(0) 
        time.sleep(0.1)

# Start button listening thread
button_thread = threading.Thread(target=button_listener)
button_thread.daemon = True  
button_thread.start()

if __name__ == '__main__':
    g_debug = False
    show_controller_help()
    if len(sys.argv) > 1:
        if str(sys.argv[1]) == "debug":
            g_debug = True
    print("debug=", g_debug)

    js = XGO_Joystick(dog, debug=g_debug)
    while True:
        state = js.joystick_handle()
        if state != js.STATE_OK:
            if state == js.STATE_KEY_BREAK:
                break
            time.sleep(1)
            js.reconnect()
    del js