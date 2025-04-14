from uiutils import *
import cv2
import mediapipe as mp


button = Button()
fm = get_dog_type_cache()

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

IMAGE_FILES = []
with mp_face_detection.FaceDetection(
    model_selection=1, min_detection_confidence=0.5) as face_detection:
  for idx, file in enumerate(IMAGE_FILES):
    image = cv2.imread(file)
    results = face_detection.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    if not results.detections:
      continue
    annotated_image = image.copy()
    for detection in results.detections:
      print('Nose tip:')
      print(mp_face_detection.get_key_point(
          detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
      mp_drawing.draw_detection(annotated_image, detection)
    cv2.imwrite('/tmp/annotated_image' + str(idx) + '.png', annotated_image)

cap=cv2.VideoCapture(0)
cap.set(3,320)
cap.set(4,240)
with mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5) as face_detection:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      continue

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_detection.process(image)

    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.detections:
      for detection in results.detections:
        value_x=0
        value_y=0
        mp_drawing.draw_detection(image, detection)
        xy=(mp_face_detection.get_key_point(detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
        face_x=320-xy.x*320
        face_y=xy.y*240
        value_x = face_x - 160
        value_y = face_y - 120
        rider_x=value_x
        print(face_x,face_y)
        if value_x > 55:
          value_x = 55
        elif value_x < -55:
          value_x = -55
        if value_y > 75:
          value_y = 75
        elif value_y < -75:
          value_y = -75
          
    else:
      value_x=value_y=face_x=face_y=0
      rider_x=9999
    print(['y','p'],[value_x/9, value_y/15])
    print(value_x,value_y)
    print(fm[2])
    if rider_x==9999:
      dog.rider_turn(0)
    else:
      if rider_x > 35:
        dog.rider_turn(20)
      elif rider_x < -35:
        dog.rider_turn(-20)
      else:
        dog.rider_turn(0)
    b,g,r = cv2.split(image)
    image = cv2.merge((r,g,b))
    image = cv2.flip(image, 1)
    imgok = Image.fromarray(image)
    display.ShowImage(imgok)
    if cv2.waitKey(5) & 0xFF == 27:
      break
    if button.press_b():
      dog.reset()
      break
cap.release()
