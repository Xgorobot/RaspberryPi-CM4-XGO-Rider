
'''
密钥需要环境中获取
language_recognize.py中也有一个密钥需要配置
语音控制运动，需要在联网情况下运行
每次命令需要用“你好，lulu”唤醒，然后开始给命令，支持前进，后退，左转，右转，
以及趴下,站起,转圈,匍匐前进,原地踏步,蹲起,沿x转动,沿y转动,沿z转动,三轴转动,撒尿,坐下,招手,伸懒腰,波浪运动,摇摆运动,求食,找食物,握手,展示机械臂,俯卧撑，张望，跳舞，调皮
如需添加其他功能，可以在大模型调用的prompt给出，并同步修改后续运动
可视化相关的已经注释掉
'''
#-Large model call-#
import os
import ast
from volcenginesdkarkruntime import Ark
def model_output(content):
    #api_key = os.getenv('API_KEY')
    api_key = '67e1719b-fc92-43b7-979d-3692135428a4'
    model = "doubao-1.5-pro-32k-250115"
    client = Ark(api_key = api_key)
    prompt = '''
        我接下来会给你一段话，如果有退出，停止等意思，请返回字符'退出'，请根据以下规则对其进行处理，并以列表形式返回结果。列表格式为：  
        `[['x', step], ['rider_turn', yaw], ...]`，各元素的含义如下：  
        1. 'x'：表示前后移动。  
           - `step` 为正时，表示向前移动的距离  
           - `step` 为负时，表示向后移动的距离   
        2. 'rider_turn'：表示转向。  
           - 'yaw'：为正时，表示向左转动的角度
           - 'yaw'：为负时，表示向右转动的角度
        3. action
           - id:取值范围为1-6,分别对应[左右摇摆,高低起伏,前进后退,四方蛇形,升降旋转,圆周晃动]。举例说明，即左右摇摆的id为1,四方蛇形为4,圆周晃动为6
       **默认值规则**：  
        - 如果未指定移动距离，默认移动距离为 `30`。  
        - 如果未指定转动角度，默认转动角度为 `120`。 
        请严格按照上述规则处理输入内容，并返回结果列表。
    '''
    prompt = prompt + content
    # Create a dialog request
    completion = client.chat.completions.create(
        model = model,
        messages = [
            {"role": "user", "content": prompt},
        ],
    )
    result = completion.choices[0].message.content
    result = ast.literal_eval(result)
    return result
#-Wake Word Detection-#
from libnyumaya import AudioRecognition, FeatureExtractor
from auto_platform import AudiostreamSource, play_command
import time
import os
from datetime import datetime

def wake_up():
    break_luyin = False
    audio_stream = AudiostreamSource()
    libpath = "/home/pi/RaspberryPi-CM4-main/demos/EI/libnyumaya_premium.so.3.1.0"
    extractor = FeatureExtractor(libpath)
    detector = AudioRecognition(libpath)
    extactor_gain = 1.0
    keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4-main/demos/EI/lulu_v3.1.907.premium", 0.7)
    bufsize = detector.getInputDataSize()
    audio_stream.start()
    while True:
        frame = audio_stream.read(bufsize * 2, bufsize * 2)
        if not frame:
            time.sleep(0.01)
            continue
        features = extractor.signalToMel(frame, extactor_gain)
        prediction = detector.runDetection(features)
        if prediction != 0:
            now = datetime.now().strftime("%d.%b %Y %H:%M:%S")
            if prediction == keywordIdlulu:
                print("唤醒成功" + "lulu detected:" + now)
                os.system(play_command + " /home/pi/RaspberryPi-CM4-main/demos/EI/ding.wav")
                audio_stream.stop()
                return 1

import os, re
from xgolib import XGO
import cv2
import os, socket, sys, time
import spidev as SPI
from PIL import Image, ImageDraw, ImageFont
from key import Button
import threading
import json, base64
import subprocess
import pyaudio
import wave
import numpy as np
from scipy import fftpack
from datetime import datetime
from audio import start_recording  
from language_recognize import test_one

#-Dog Robot Initialization-#
dog = XGO(port='/dev/ttyAMA0', version="xgomini")
fm = dog.read_firmware()
if fm[0] == 'M':
    print('XGO-MINI')
    dog = XGO(port='/dev/ttyAMA0', version="xgomini")
    dog_type = 'M'
else:
    dog = XGO(port='/dev/ttyAMA0', version="xgolite")
    print('XGO-LITE')
    dog_type = 'L'
if dog_type == 'L':
    mintime_yaw = 0.8
    mintime_x = 0.1
else:
    mintime_yaw = 0.7
    mintime_x = 0.3
button = Button()
#-Screen Initialization-#
import xgoscreen.LCD_2inch as LCD_2inch
display = LCD_2inch.LCD_2inch()
display.clear()
splash_theme_color = (15, 21, 46)
splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
font2 = ImageFont.truetype("/home/pi/model/msyh.ttc", 16)
draw = ImageDraw.Draw(splash)
display.ShowImage(splash)

def lcd_draw_string(
    splash,
    x,
    y,
    text,
    color=(255, 255, 255),
    font_size=16,
    max_width=220,
    max_lines=5,
    clear_area=True
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
    
#-Dog Robot Speed Adjustment-#
def adaptive_move(distance):
    if distance < 15:
        speed = 10
    elif distance < 30:
        speed = 15
    else:
        speed = 20
    return speed
def adaptive_turn(yaw):
    if yaw < 20:
        turn_speed = 10
    elif yaw < 50 :
        turn_speed = 20
    else:
        turn_speed = 30
    return turn_speed

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
            stream.stop_stream()
            stream.close()
            p.terminate()
            os._exit(0)
threading.Thread(target = check_exit,daemon = True).start()        
while True:
  print("等待唤醒词")
  draw.rectangle([0, 0, display.width, display.height], fill=(15, 21, 46))  
  #Show Wake Up Call
  lcd_draw_string(
    draw,
    x=50,
    y=120,
    text="请说出lulu唤醒我",
    color=(255, 255, 255),
    font_size=32,
    max_width=200,
    max_lines=4,
    clear_area=True
  )
  display.ShowImage(splash)
    
  wake = wake_up()
  if wake:
    print("唤醒成功")
    stream.stop_stream()
    time.sleep(0.1)
    stream.start_stream()
    start_recording(p, stream)
    
  content = test_one()
  if content == 0:
    splash = Image.new("RGB", (display.height, display.width), splash_theme_color)
    draw = ImageDraw.Draw(splash)
    #Recognition Failure
    lcd_draw_string(
      draw,
      100, 50,
      "识别失败，请重试",
      color=(255, 255, 0),
      clear_area=True
      )
    display.ShowImage(splash)
    time.sleep(2)
    continue
  else:
    print(content)
    draw.rectangle([0, 0, display.width, display.height], fill=(15, 21, 46))        
    #Displaying Recognized Content
    lcd_draw_string(
      draw,
      50, 120,
      text=content,
      color=(255, 255, 255),
      clear_area=False
      )
    display.ShowImage(splash)
    result = model_output(content=content)
    if result == '退出':
      break
    for i in result:
      if i[0] == 'x':
        speed = adaptive_move(int(i[1]))
        dog.move_x(i[0], speed * int(i[1]) / abs(int(i[1])))
        time.sleep(abs(int(i[1] / speed)))
        dog.stop()
        time.sleep(0.5)
      if i[0] == 'rider_turn':
        turn_speed = adaptive_turn(int(i[1]))
        dog.rider_turn(turn_speed * int(i[1]) / abs(int(i[1])))
        time.sleep(abs(int(i[1] / turn_speed)))
        dog.stop()
        time.sleep(0.5)
      if i[0] == 'action':
        dog.action(int(i[1]))
        time.sleep(10)
        dog.stop()
        time.sleep(0.5)
