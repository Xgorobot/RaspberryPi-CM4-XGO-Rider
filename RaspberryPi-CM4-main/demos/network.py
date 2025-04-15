from robot import *
import numpy as np
import pyzbar.pyzbar as pyzbar
import cv2
from PIL import Image, ImageDraw, ImageFont
import os
import time
import sys
import re

# Init Key
button = Button()
# Language Loading
la = load_language()

def cv2AddChineseText(img, text, position, textColor=(200, 0, 200), textSize=10):
    if isinstance(img, np.ndarray):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype("/home/pi/model/msyh.ttc", textSize, encoding="utf-8")
    draw.text(position, text, textColor, font=fontStyle)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

def makefile(s, p):
    t1 = '''
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CN

network={
    ssid="'''
    t2 = '''
    key_mgmt=WPA-PSK
    }
    '''
    t3 = '''"
    psk="'''
    files = t1 + s + t3 + p + '"' + t2
    print("Generated wpa_supplicant content:")
    print(files)
    return files

def parse_wifi_config(content):
    try:
        # 使用正则表达式匹配
        ssid_match = re.search(r'ssid="([^"]*)"', content)
        pwd_match = re.search(r'psk="([^"]*)"', content)
        
        ssid = ssid_match.group(1) if ssid_match else "XGO2"
        pwd = pwd_match.group(1) if pwd_match else "LuwuDynamics"
        
        print(f"Parsed WiFi config - SSID: {ssid}, PWD: {pwd}")
        return ssid, pwd
    except Exception as e:
        print(f"Error parsing wifi config: {str(e)}")
        return "XGO2", "LuwuDynamics"

font = cv2.FONT_HERSHEY_SIMPLEX
cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)

if not cap.isOpened():
    print("[camera.py:cam]:can't open this camera")
    sys.exit(1)

wifi = "/etc/wpa_supplicant/wpa_supplicant.conf"

# 读取并解析现有WiFi配置
try:
    with open(wifi, 'r') as f:
        content = f.read()
        print("Current wifi config file content:")
        print(content)
        ssid, pwd = parse_wifi_config(content)
except Exception as e:
    print(f"Error reading wifi config: {str(e)}")
    ssid, pwd = "XGO2", "LuwuDynamics"

while True:
    try:
        ret, img = cap.read()
        if not ret:
            print("Failed to capture image")
            time.sleep(0.1)
            continue
            
        img_ROI_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(img_ROI_gray)

        if len(barcodes) == 0:
            print('No QR code detected')
            text = "{}".format(la['NETWORK']['NOQR'])
            img = cv2AddChineseText(img, text, (55, 30), (255, 0, 0), 25)
        else:
            for barcode in barcodes:
                try:
                    barcodeData = barcode.data.decode("utf-8")
                    print(f"Decoded QR: {barcodeData}")
                    
                    if not barcodeData:
                        continue
                        
                    # 解析二维码数据
                    a = barcodeData.find("S:")
                    b = barcodeData.find("T:")
                    c = barcodeData.find("P:")
                    
                    if a == -1 or c == -1:
                        print("Invalid QR format - missing S: or P:")
                        continue
                        
                    # 提取SSID
                    if b > a and b != -1:
                        SSID = barcodeData[a + 2:b - 1] 
                    else:
                        SSID = barcodeData[a + 2:c - 1] 
                    
                    # 提取密码
                    d = barcodeData.find("H:")
                    e = len(barcodeData)
                    if d != -1:
                        PWD = barcodeData[c + 2:d - 1]
                    else:
                        PWD = barcodeData[c + 2:e]
                    
                    print(f"Extracted WiFi info - SSID: {SSID}, PWD: {PWD}")
                    
                    # 生成并写入配置文件
                    fc = makefile(SSID, PWD)
                    try:
                        with open(wifi, 'w') as f:
                            f.write(fc)
                        text = "{}".format(la['NETWORK']['SUCCESS'])
                        img = cv2AddChineseText(img, text, (10, 30), (0, 255, 0), 18)
                        os.system("sudo wpa_cli -i wlan0 reconfigure")
                        
                        # 显示结果图像
                        b, g, r = cv2.split(img)
                        img = cv2.merge((r, g, b))
                        imgok = Image.fromarray(img)
                        display.ShowImage(imgok)
                        
                        time.sleep(4)
                        sys.exit(0)
                    except Exception as e:
                        print(f"Error writing wifi config: {str(e)}")
                        
                except Exception as e:
                    print(f"Error processing QR code: {str(e)}")

        # 显示图像
        b, g, r = cv2.split(img)
        img = cv2.merge((r, g, b))
        imgok = Image.fromarray(img)
        display.ShowImage(imgok)

        # 按钮处理
        if button.press_c():
            print("Button C pressed - resetting to default WiFi")
            ssid = 'XGO2'
            pwd = 'LuwuDynamics'
            fc = makefile(ssid, pwd)
            try:
                with open(wifi, 'w') as f:
                    f.write(fc)
                os.system("sudo wpa_cli -i wlan0 reconfigure")
            except Exception as e:
                print(f"Error resetting WiFi: {str(e)}")

        if (cv2.waitKey(1)) == ord('q'):
            break
        if button.press_b():
            break

    except Exception as e:
        print(f"Main loop error: {str(e)}")
        time.sleep(1)

cap.release()
print("Program exited")
