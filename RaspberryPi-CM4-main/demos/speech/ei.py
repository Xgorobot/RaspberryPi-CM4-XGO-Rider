import random
import os, re
import socket, sys, time
import spidev as SPI
import xgoscreen.LCD_2inch as LCD_2inch
from xgolib import XGO
from PIL import Image, ImageDraw, ImageFont
import threading
import json, base64
import subprocess
import pyaudio
import wave
import numpy as np
from scipy import fftpack
from datetime import datetime
from key import Button
import requests
from audio_ei import start_recording
from language_recognize import test_one
from doubao_ei import model_output
import logging
from key import language
la=language()
SPLASH_COLOR = (15, 21, 46)
FONT_PATH = "/home/pi/model/msyh.ttc"
FONT_SIZE = 20
DOG_PORT = '/dev/ttyAMA0'
DOG_VERSION = "xgorider"
TEST_NETWORK_URL = "http://www.baidu.com"

WIFI_OFFLINE_PATH = "/home/pi/RaspberryPi-CM4-main/pics/offline.png"
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 22)
color_white = (255, 255, 255)
mic_purple = (24, 47, 223)

ACTION_MAP = {
    "Dance": (23, 6),
    "Pushups": (21, 8),
    "Pee": (11, 7),
    "Stretch": (14, 10),
    "Pray": (19, 3),
    "Chickenhead": (20, 9),
    "Lookforfood": (17, 4),
    "Grabdownwards": (130, 10),
    "Wave": (15, 6),
    "Beg": (17, 3)
}
import pyaudio
from auto_platform import AudiostreamSource

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000


class GPTCMD:
    def __init__(self):

        self.display = LCD_2inch.LCD_2inch()
        self.display.Init()
        self.splash_theme_color = (15, 21, 46)
        self.splash = Image.new("RGB", (self.display.height, self.display.width), SPLASH_COLOR)
        self.draw = ImageDraw.Draw(self.splash)
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

        self.rider = XGO("xgorider")
        self.button = Button()
        self.audio_stream = None
        self.stream_a = None
        self.p = None
        self.network_available = False


        # 启动按键检测线程
        self._start_button_thread()
        try:
            wifi_img = Image.open(WIFI_OFFLINE_PATH)
            self.nowifi_image = Image.new("RGB", wifi_img.size, SPLASH_COLOR)
            self.nowifi_image.paste(wifi_img, (0, 0), wifi_img)  
        except Exception as e:
            print(f"加载图片失败: {e}")
            self.nowifi_image = Image.new("RGB", (100, 100), (255, 0, 0))  

    def visual(self, content):
        mic_logo = Image.open("/home/pi/RaspberryPi-CM4-main/pics/mic.png")
        mic_purple = (24, 47, 223)
        splash = Image.new("RGB", (self.display.height, self.display.width), self.splash_theme_color)
        draw = ImageDraw.Draw(splash)
        draw.rectangle([0, 0, self.display.width, self.display.height], fill=(15, 21, 46))
        gray_color = (128, 128, 128)

        def draw_cir(ch):
            if ch > 15:
                ch = 15
            draw.bitmap((145, 40), mic_logo, mic_purple)
            radius = 4
            cy = 60
            centers = [(62, cy), (87, cy), (112, cy), (210, cy), (235, cy), (260, cy)]
            for center in centers:
                random_offset = random.randint(0, ch)
                new_y = center[1] + random_offset
                new_y2 = center[1] - random_offset

                draw.line([center[0], new_y2, center[0], new_y], fill=mic_purple, width=11)

                top_left = (center[0] - radius, new_y - radius)
                bottom_right = (center[0] + radius, new_y + radius)
                draw.ellipse([top_left, bottom_right], fill=mic_purple)
                top_left = (center[0] - radius, new_y2 - radius)
                bottom_right = (center[0] + radius, new_y2 + radius)
                draw.ellipse([top_left, bottom_right], fill=mic_purple)

        def draw_wave(ch):
            if ch > 10:
                ch = 10
            start_x = 40
            start_y = 32
            width, height = 80, 50
            y_center = height // 2
            current_y = y_center
            previous_point = (0 + start_x, y_center + start_y)
            draw.bitmap((145, 40), mic_logo, mic_purple)
            x = 0
            while x < width:
                segment_length = random.randint(7, 25)
                gap_length = random.randint(4, 20)

                for _ in range(segment_length):
                    if x >= width:
                        break
                    amplitude_change = random.randint(-ch, ch)
                    current_y += amplitude_change
                    if current_y < 0:
                        current_y = 0
                    elif current_y > height - 1:
                        current_y = height - 1
                    current_point = (x + start_x, current_y + start_y)
                    draw.line([previous_point, current_point], fill=mic_purple)
                    previous_point = current_point
                    x += 1
                for _ in range(gap_length):
                    if x >= width:
                        break
                    current_point = (x + start_x, y_center + start_y)
                    draw.line([previous_point, current_point], fill=mic_purple, width=2)
                    previous_point = current_point
                    x += 1
            start_x = 210
            start_y = 32
            width, height = 80, 50
            y_center = height // 2
            current_y = y_center
            previous_point = (0 + start_x, y_center + start_y)
            draw.rectangle(
                [(start_x - 1, start_y), (start_x + width, start_y + height)],
                fill=self.splash_theme_color,
            )
            x = 0
            while x < width:
                segment_length = random.randint(7, 25)
                gap_length = random.randint(4, 20)
                for _ in range(segment_length):
                    if x >= width:
                        break
                    amplitude_change = random.randint(-ch, ch)
                    current_y += amplitude_change
                    if current_y < 0:
                        current_y = 0
                    elif current_y > height - 1:
                        current_y = height - 1
                    current_point = (x + start_x, current_y + start_y)
                    draw.line([previous_point, current_point], fill=mic_purple)
                    previous_point = current_point
                    x += 1
                for _ in range(gap_length):
                    if x >= width:
                        break
                    current_point = (x + start_x, y_center + start_y)
                    draw.line([previous_point, current_point], fill=mic_purple, width=2)
                    previous_point = current_point
                    x += 1

        draw_wave(5)
        rectangle_x = (self.display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 110  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 80
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)

        def lcd_draw_string(
                splash,
                x,
                y,
                text,
                color=(255, 255, 255),
                font_size=16,
                max_width=220,
                max_lines=5,
                clear_area=False
        ):
            font = ImageFont.truetype("/home/pi/model/msyh.ttc", font_size)

            line_height = font_size + 2
            total_height = max_lines * line_height

            if clear_area:
                draw.rectangle((x, y, x + max_width, y + total_height), fill=(15, 21, 46))
            lines = []
            current_line = ""
            for char in text:
                test_line = current_line + char
                if font.getlength(test_line) <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            if max_lines:
                lines = lines[:max_lines]

            for i, line in enumerate(lines):
                splash.text((x, y + i * line_height), line, fill=color, font=font)

        lcd_draw_string(
            draw,
            x=70,
            y=115,
            text=content,
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        self.display.ShowImage(splash)
    def _start_button_thread(self):
        def check_button():
            while True:
                if self.button.press_b():
                    try:
                        self.audio_stream.stop()
                        logging.warning('audio_stream kill')
                    except Exception as e:
                        logging.warning(e)
                    self.rider.rider_reset()
                    try:
                        self.stream_a.stop_stream()
                        self.stream_a.close()
                        logging.warning("stream_a kill")
                    except Exception as e:
                        logging.warning(e)
                    try:
                        self.p.terminate()
                        logging.warning("p terminate")
                    except:
                        pass
                    print("B键按下, 退出程序")
                    os._exit(0)
                time.sleep(0.1)

        thread = threading.Thread(target=check_button, daemon=True)
        thread.start()

    def show_message(self, text, color=(255, 255, 255)):
        self.draw.rectangle((0, 0, self.display.height, self.display.width), fill=SPLASH_COLOR)
        self.draw.text((80, 100), text, fill=color, font=self.font)
        self.display.ShowImage(self.splash)

    def execute_action(self, action_name):
        if action_name in ACTION_MAP:
            action_id, duration = ACTION_MAP[action_name]
            self.dog.action(action_id)
            time.sleep(duration)
            return True
        return False

    def check_network(self):
        max_attempts = 5
        attempt = 0
        
        while attempt < max_attempts:
            try:
                requests.get(TEST_NETWORK_URL, timeout=1)
                print("Net is connected")
                self.network_available = True
                return True  # 直接返回True，不显示任何内容
            except:
                print(f"Network connection attempt {attempt + 1} failed")
                attempt += 1
                time.sleep(1)
        
        print("Network connection failed after 5 attempts")
        self.network_available = False
        self.draw.rectangle((0, 0, self.display.height, self.display.width), fill=SPLASH_COLOR)
        img_width, img_height = self.nowifi_image.size
        x_pos = (self.display.height - img_width) // 2
        y_pos = 40
        self.splash.paste(self.nowifi_image, (x_pos, y_pos))
        if la == "cn":
            text = "WIFI未连接或无网络"
        else:
            text = "WIFI is not connected"
        text_width = self.draw.textlength(text, font=font2)
        x_position = (self.display.height - text_width) // 2
        self.draw.text((x_position, 170), text, fill=color_white, font=font2)
        self.display.ShowImage(self.splash)
        
        return False

    def run(self):
        if not self.check_network():
            while True:
                time.sleep(1)
            return
        
        if la == "cn":
            self.show_message("正在启动，请稍后", color=(255, 255, 255))
        else:
            self.show_message("Starting up...", color=(255, 255, 255))

        while True:
            self.p = pyaudio.PyAudio()
            self.stream_a = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )
            self.audio_stream = AudiostreamSource()
            logging.warning('音频初始化完成')
            start_recording(self.p, self.stream_a, self.audio_stream)
            logging.warning("录音结束")
            if la=="cn":
              self.visual(content="指令识别中，请稍等")
            else:
              self.visual(content="Instruction recognizing...")
            content = test_one()
            logging.warning(f"识别内容: {content}")

            if not content:
                logging.warning("录音出错")
                continue

            action_results = model_output(content=content)
            logging.warning(action_results)
            self.visual(content=content)
            try:
                for i in action_results:
                    print(i[0])
                    if i[0] == 'move':
                        speed = int(i[1][0])
                        move_time = int(i[1][1])
                        self.rider.rider_move_x(speed, move_time)
                    elif i[0] == 'turn':
                        speed = int(i[1][0])
                        turn_time = int(i[1][1])
                        self.rider.rider_turn(speed, turn_time)
                    elif i[0] == 'height':
                        self.rider.rider_height(int(i[1]))
                        time.sleep(1.5)
                    elif i[0] == 'roll':
                        self.rider.rider_roll(int(i[1]))
                    elif i[0] == 'periodic_z':
                        self.rider.rider_periodic_z(int(i[1][0]))
                        time.sleep(int(i[1][1]))
                        self.rider.rider_periodic_z(0)
                    elif i[0] == 'periodic_roll':
                        self.rider.rider_periodic_roll(int(i[1][0]))
                        time.sleep(int(i[1][1]))
                        self.rider.rider_periodic_z(0)
                    elif i[0] == 'reset':
                        self.rider.rider_reset()
                    elif i[0] == 'action':
                        action_list = {"左右摇摆":1,"高低起伏":2,"前进后退":3, "四方蛇形":4, "升降旋转":5 ,"圆周晃动":6}
                        a = action_list[i[1]]
                        self.rider.rider_action(int(a))
                        time_list = [3, 4, 3, 4, 6, 5]
                        action_time = time_list[int(a) - 1]
                        time.sleep(action_time)
                        self.rider.reset()
                    elif i[0] == 'led':
                        color = [int(i[1][1]), int(i[1][2]), int(i[1][3])]
                        self.rider.rider_led(int(i[1][0]), color)
                    elif i[0] == 'balance':
                        self.rider.rider_balance_roll(int(i[1]))
                    elif i[0] == 'perform':
                        self.rider.rider_perform(int(i[1]))
                        time.sleep(10)
                        self.rider.rider_perform(0)
                    elif i[0] == '重试':
                        continue
                    elif i[0] == '退出':
                        try:
                            self.audio_stream.stop()
                            logging.warning('audio_stream kill')
                        except Exception as e:
                            logging.warning(e)
                        self.rider.rider_reset()
                        try:
                            self.stream_a.stop_stream()
                            self.stream_a.close()
                            logging.warning("stream_a kill")
                        except Exception as e:
                            logging.warning(e)
                        try:
                            self.p.terminate()
                            logging.warning("p terminate")
                        except:
                            pass
                        self.rider.rider_reset()
                        time.sleep(1)
                        print('退出')
                        exit()
                    else:
                        continue
            except Exception as e:
                logging.warning(f'发生未知错误: {e}')
                self.visual(content="指令识别错误，请重试")
                time.sleep(2)
                continue


if __name__ == "__main__":
    controller = GPTCMD()
    controller.run()
