import cv2
from uiutils import *
import numpy as np
import pyzbar.pyzbar as pyzbar
import time
from PIL import Image, ImageDraw, ImageFont

button = Button()

cap = cv2.VideoCapture(0)
cap.set(3, 320)
cap.set(4, 240)


last_barcode_data = None
last_text_overlay = None

def cv2AddChineseText(img, text, position, textColor=(0, 255, 0), textSize=20, max_width=110):
    if isinstance(img, np.ndarray):  
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    

    try:
        fontStyle = ImageFont.truetype("/home/pi/model/msyh.ttc", textSize, encoding="utf-8")
    except:
        fontStyle = ImageFont.load_default()
    

    chars_per_line = max_width // (textSize // 2)
    lines = []
    current_line = ""
    for char in text:
        if len(current_line.encode('utf-8')) + len(char.encode('utf-8')) <= chars_per_line * 2:
            current_line += char
        else:
            lines.append(current_line)
            current_line = char
    if current_line:
        lines.append(current_line)
    
    x, y = position
    for line in lines:
        draw.text((x, y), line, textColor, font=fontStyle)
        y += textSize + 5
    
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

if not cap.isOpened():
    print("[camera.py:cam]:can't open this camera")

fps = 30
frame_delay = int(1000/fps)

while True:
    start_time = time.time()
    ret, img = cap.read()
    
    if not ret:
        continue
    
    display_img = img.copy()
    img_ROI_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    barcodes = pyzbar.decode(img_ROI_gray)
    
    current_barcode_data = None
    for barcode in barcodes:
        try:

            barcodeData = barcode.data.decode('utf-8')
        except UnicodeDecodeError:
            try:

                barcodeData = barcode.data.decode('gbk')
            except:

                barcodeData = str(barcode.data)
        
        barcodeType = barcode.type
        current_barcode_data = barcodeData
        
        if barcodeData != last_barcode_data:
            print(f"[INFO] Found {barcodeType} barcode: {barcodeData}")
            
            text_overlay = np.zeros_like(img)
            text_overlay = cv2AddChineseText(text_overlay, barcodeData, (10, 30), (0, 255, 0), 30)
            
            last_text_overlay = text_overlay
            last_barcode_data = barcodeData
    
    if last_text_overlay is not None:
        display_img = cv2.addWeighted(img, 1, last_text_overlay, 1, 0)
    
    display_img = cv2.cvtColor(display_img, cv2.COLOR_BGR2RGB)
    imgok = Image.fromarray(display_img)
    display.ShowImage(imgok)
    
    elapsed = (time.time() - start_time) * 1000
    remaining_delay = max(1, frame_delay - int(elapsed))
    if cv2.waitKey(remaining_delay) == ord('q'):
        break
    if button.press_b():
        break

cap.release()
