from subprocess import Popen
from demos.uiutils import *

#IniT Key
button = Button()
fm = get_dog_type_cache()
print(fm)

#Play Music
proc = Popen("mplayer ./demos/music/Dream.mp3 -loop 0", shell=True)

#PIC PATH
pic_path = "./demos/expression/"

def show_rider(expression_name_cs, pic_num):
    global canvas
    for i in range(0, pic_num):
        exp = Image.open(
            pic_path
            + "rider/"
            + expression_name_cs
            + "/"
            + expression_name_cs
            + str(i + 1)
            + ".png"
        )
        display.ShowImage(exp)
        time.sleep(0.01)
        if button.press_b():
            dog.perform(0)
            sys.exit()

dog.perform(1)

#Play Music
proc = Popen("mplayer ./demos/music/Dream.mp3 -loop 0", shell=True)

while 1:
        print(fm[1])
        show_rider("like", 83)
        show_rider("sad", 65)
        show_rider("Angry", 55)
        show_rider("cute", 76)
        show_rider("doubt", 64)
        show_rider("embarrassed", 66)
        show_rider("grievance", 72)
        show_rider("hate", 81)
        show_rider("laugh", 51)
        show_rider("shy", 60)
        show_rider("sleep", 94)
        show_rider("surprised", 74)
        show_rider("vertigo", 59)
dog.perform(0)
proc.kill()
