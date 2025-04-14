from libnyumaya import AudioRecognition, FeatureExtractor
from auto_platform import AudiostreamSource,play_command
import time
import os
from datetime import datetime
automark = 1
quitmark = 0
def wake_up():
        break_luyin = False
        audio_stream = AudiostreamSource()
        libpath = "/home/pi/RaspberryPi-CM4/move_auto/libnyumaya_premium.so.3.1.0"
        extractor = FeatureExtractor(libpath)
        detector = AudioRecognition(libpath)
        extactor_gain = 1.0
        # Add one or more keyword models
        keywordIdlulu = detector.addModel("/home/pi/RaspberryPi-CM4/move_auto/lulu_v3.1.907.premium", 0.6)
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
                    
                    print("唤醒成功"+"lulu detected:" + now)
                    # os.system(play_command + " /home/pi/RaspberryPi-CM4/move_auto/ding.wav")
                    audio_stream.stop()
                    return 1
