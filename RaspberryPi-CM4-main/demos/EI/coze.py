
'''
密钥需要环境中获取
language_recognize.py中也有一个密钥需要配置
语音控制运动，需要在联网情况下运行
每次命令需要用“你好，lulu”唤醒，然后开始给命令，支持前进，后退，左转，右转，
以及趴下,站起,转圈,匍匐前进,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手,伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮
如需添加其他功能，可以在大模型调用的prompt给出，并同步修改后续运动
可视化相关的已经注释掉
'''
from PIL import Image, ImageDraw, ImageFont
import xgoscreen.LCD_2inch as LCD_2inch
import logging
display = LCD_2inch.LCD_2inch()
display.clear()
splash_theme_color = (15, 21, 46)
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

import sys

# 获取 vosk 模块的安装路径，根据实际情况修改
vosk_path = '/home/pi/.local/lib/python3.9/site-packages'

# 检查路径是否已经在 sys.path 中，如果不在则添加
if vosk_path not in sys.path:
    sys.path.append(vosk_path)
#-Large model call-#
import os
import ast
from volcenginesdkarkruntime import Ark
from cozepy import Coze, TokenAuth, BotPromptInfo, Message, ChatEventType, MessageContentType, \
    COZE_CN_BASE_URL  # 忽略代码检查工具对该行import的警告
def model_output(content):
    coze_api_token = 'pat_rdTYS4U5jVUlnNfEWVPFl7TwmrWtw3Im9IBEzZedR6hVPp5bHfV41e9ewjsk7Xw3'

    # 初始化Coze客户端
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=COZE_CN_BASE_URL)

    bot_id = '7501211586074509339'
    user_id = '123'
    # 调用coze.chat.stream方法创建一个聊天会话。此创建方法是流式聊天，会返回一个聊天迭代器。
    # 开发者应迭代该迭代器以获取聊天事件并进行处理
    chat_poll = coze.chat.create_and_poll(
        bot_id=bot_id,
        user_id=user_id,
        additional_messages=[
            # 构建用户提问消息
            Message.build_user_question_text(content)
        ],
    )
    result = chat_poll.messages[0].content
    result = ast.literal_eval(result)
    return result

#-Wake Word Detection-#
from libnyumaya import AudioRecognition, FeatureExtractor
from auto_platform import AudiostreamSource, play_command
import time
import os
from datetime import datetime

from vosk import Model, KaldiRecognizer
model_path = "/home/pi/RaspberryPi-CM4-main/demos/EI/vosk-model-small-cn-0.22/"
wake_word1 = "你好"  
wake_word2 = '您好'
model = Model(model_path)

# def wake_up(stream, rate, chunk_size):
#     break_luyin = False
#     audio_stream = AudiostreamSource()
#     libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/src/libnyumaya_premium.so.3.1.0"
#     extractor = FeatureExtractor(libpath)
#     detector = AudioRecognition(libpath)
#     extactor_gain = 1.0
#     keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/src/lulu_v3.1.907.premium", 0.7)
#     bufsize = detector.getInputDataSize()
#     rec = KaldiRecognizer(model, rate)
#     audio_stream.start()
#     while True:
#         frame = audio_stream.read(bufsize * 2, bufsize * 2)
#         data = stream.read(chunk_size)
#         if rec.AcceptWaveform(data):
#             result = rec.Result()
#             text = eval(result)["text"]
#             print(text)
#             if wake_word1 in text or wake_word2 in text:
#                 print("唤醒词已检测到！")
#                 return 1
#         if not frame:
#             time.sleep(0.01)
#             continue
#         features = extractor.signalToMel(frame, extactor_gain)
#         prediction = detector.runDetection(features)
#         if prediction != 0:
#             now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
#             if prediction == keywordIdlulu:
#                 print("唤醒成功" + "lulu detected:" + now)
#                 #os.system(play_command + " /home/pi/RaspberryPi-CM4-main/demos/src/ding.wav")
#                 return 1
def wake_up(p, rate, chunk_size):
    break_luyin = False
    audio_stream = AudiostreamSource()
    libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/src/libnyumaya_premium.so.3.1.0"
    extractor = FeatureExtractor(libpath)
    detector = AudioRecognition(libpath)
    extactor_gain = 1.0
    keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/src/lulu_v3.1.907.premium", 0.7)
    bufsize = detector.getInputDataSize()
    audio_stream.start()
    rec = KaldiRecognizer(model, rate)

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk_size)

    while True:
        try:
            frame = audio_stream.read(bufsize * 2, bufsize * 2)
            data = stream.read(chunk_size, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = rec.Result()
                text = eval(result)["text"]
                print(text)
                if wake_word1 in text or wake_word2 in text:
                    print("唤醒词已检测到！")
                    stream.stop_stream()
                    stream.close()
                    return 1
            if not frame:
                time.sleep(0.01)
                continue
            features = extractor.signalToMel(frame, extactor_gain)
            prediction = detector.runDetection(features)
            if prediction != 0:
                now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
                if prediction == keywordIdlulu:
                    print("唤醒成功" + "lulu detected:" + now)
                    # os.system(play_command + " /home/pi/RaspberryPi-CM4-main/demos/src/ding.wav")
                    audio_stream.stop()
                    stream.stop_stream()
                    stream.close()
                    return 1
            time.sleep(0.01)  # 降低睡眠时间，提高读取频率
        except OSError as e:
            if e.errno == -9981:
                print("Input overflowed, cleaning buffer...")
                stream.stop_stream()
                stream.close()
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=rate,
                                input=True,
                                frames_per_buffer=chunk_size)
            else:
                raise

    return 0



time_list = [3, 4, 3, 4, 6, 5]
import os, re
from xgolib import XGO
import cv2
import os, socket, sys, time
import spidev as SPI
from key import Button
import threading
import json, base64
import subprocess
import pyaudio
import wave
import numpy as np
from datetime import datetime
from audio import start_recording  
from language_recognize import test_one

#-Dog Robot Initialization-#
rider = XGO("xgorider")
button = Button()
#-Screen Initialization-#


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



p = pyaudio.PyAudio()
#-Record parameter-#
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
def check_exit():
    while True:
        if button.press_b():
            print("Button B Pressed")
            try:
                stream.stop_stream()
                stream.close()
            except Exception as e:
                print('音频流未打开')
            p.terminate()
            os._exit(0)
threading.Thread(target = check_exit,daemon = True).start()        
while True:
  print("等待唤醒词")
  splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
  draw = ImageDraw.Draw(splash)
  draw.rectangle([0, 0, display.width, display.height], fill=(15, 21, 46))
  text_color = (255, 255, 255)
  color = (102, 178, 255)
  gray_color = (128, 128, 128)
  rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
  rectangle_y = 50  # 矩形条y坐标
  rectangle_width = 200
  rectangle_height = 30
  draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height), fill=color)
  draw.text((rectangle_x + 70, rectangle_y + 5), '等待唤醒', fill=text_color, font=font2)
  rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
  rectangle_y = 100  # 矩形条y坐标
  rectangle_width = 200
  rectangle_height = 100
  draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                 fill=gray_color)
  lcd_draw_string(
      draw,
      x=70,
      y=105,
      text="请说“你好,lulu”",
      color=(255, 255, 255),
      font_size=16,
      max_width=190,
      max_lines=5,
      clear_area=False
  )
  display.ShowImage(splash)
  wake = wake_up(p,RATE,CHUNK)
  if wake:
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    text_color = (255, 255, 255)
    color = (102, 178, 255)
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 50  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 30
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=color)
    draw.text((rectangle_x + 70, rectangle_y + 5), '下达指令', fill=text_color, font=font2)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 100  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 100
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    lcd_draw_string(
        draw,
        x=70,
        y=105,
        text="唤醒成功,请给出运动指令",
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    print("唤醒成功")
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    stream.stop_stream()
    time.sleep(0.1)
    stream.start_stream()
    start_recording(p, stream)
    #start_recording()
  try:
    content = test_one()
    print(content)
  except Exception as e:
    print(f'发生未知错误: {e}')
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    text_color = (255, 255, 255)
    color = (102, 178, 255)
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 50  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 30
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=color)
    draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 100  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 100
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    lcd_draw_string(
        draw,
        x=70,
        y=105,
        text="语音识别错误，请重试",
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    time.sleep(2)
    continue
  if content == 0:
    print('识别失败')
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    text_color = (255, 255, 255)
    color = (102, 178, 255)
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 50  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 30
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=color)
    draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 100  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 100
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    lcd_draw_string(
        draw,
        x=70,
        y=105,
        text="语音识别错误，请重试",
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    time.sleep(2)
    continue
  else:
    print(content)
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    text_color = (255, 255, 255)
    color = (102, 178, 255)
    gray_color = (128, 128, 128)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 50  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 30
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=color)
    draw.text((rectangle_x + 70, rectangle_y + 5), '指令内容', fill=text_color, font=font2)
    rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
    rectangle_y = 100  # 矩形条y坐标
    rectangle_width = 200
    rectangle_height = 100
    draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                   fill=gray_color)
    lcd_draw_string(
        draw,
        x=70,
        y=105,
        text=content,
        color=(255, 255, 255),
        font_size=16,
        max_width=190,
        max_lines=5,
        clear_area=False
    )
    display.ShowImage(splash)
    try:
        result = model_output(content=content)
        logging.warning(result)
    except Exception as e:
        print(f'发生未知错误: {e}')
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '识别错误', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text="指令识别错误，请重试",
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        time.sleep(2)
        continue
    try:
        for i in result:
          print(i[0])
          if i[0] == 'move':
              speed = int(i[1][0])
              move_time = int(i[1][1])
              rider.rider_move_x(speed, move_time)
          elif i[0] == 'turn':
              speed = int(i[1][0])
              turn_time = int(i[1][1])
              rider.rider_turn(speed, turn_time)
          elif i[0] == 'height':
              rider.rider_height(int(i[1]))
          elif i[0] == 'roll':
              rider.rider_roll(int(i[1]))
          elif i[0] == 'periodic_z':
              rider.rider_periodic_z(int(i[1][0]))
              time.sleep(int(i[1][1]))
              rider.rider_periodic_z(0)
          elif i[0] == 'periodic_roll':
              rider.rider_periodic_roll(int(i[1]))
              time.sleep(int(i[1][1]))
              rider.rider_periodic_z(0)
          elif i[0] == 'reset':
              rider.rider_reset()
          elif i[0] == 'action':
              rider.rider_action(int(i[1]))
              action_time = time_list[int(i[1])-1]
              time.sleep(action_time)
              rider.reset()
          elif i[0] == 'led':
              color = [int(i[1][1]), int(i[1][2]), int(i[1][3])]
              rider.rider_led(int(i[1][0]), color)
          elif i[0] == 'balance':
              rider.rider_balance_roll(int(i[1]))
          elif i[0] == 'perform':
              rider.rider_perform(int(i[1]))
              time.sleep(10)
              rider.rider_perform(0)
          elif i[0] == '重试':
              continue
          elif i[0] == '退出':
              print('退出')
              if stream:
                  stream.stop_stream()
                  stream.close()
              if p:
                  p.terminate()
              exit()
          else:
            continue
    except Exception as e:
        print(f'发生未知错误: {e}')
        splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
        draw = ImageDraw.Draw(splash)
        text_color = (255, 255, 255)
        color = (102, 178, 255)
        gray_color = (128, 128, 128)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 50  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 30
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=color)
        draw.text((rectangle_x + 70, rectangle_y + 5), '指令错误', fill=text_color, font=font2)
        rectangle_x = (display.width - 120) // 2  # 矩形条居中的x坐标
        rectangle_y = 100  # 矩形条y坐标
        rectangle_width = 200
        rectangle_height = 100
        draw.rectangle((rectangle_x, rectangle_y, rectangle_x + rectangle_width, rectangle_y + rectangle_height),
                       fill=gray_color)
        lcd_draw_string(
            draw,
            x=70,
            y=105,
            text="指令识别错误，请重试",
            color=(255, 255, 255),
            font_size=16,
            max_width=190,
            max_lines=5,
            clear_area=False
        )
        display.ShowImage(splash)
        time.sleep(2)
        continue


