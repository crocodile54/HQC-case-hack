from gpiozero import Button
from picamera import PiCamera
from signal import pause
import subprocess
import time

b_bot1 = Button(27)
b_top4 = Button(17)
b_2 = Button(22)
b_3 = Button(23)
b_ext = Button(12)

video = False
burst = False

camera = PiCamera()
camera.rotation = 270
camera.start_preview(fullscreen=False,window=(0,10,580,480))
prev_active = True
video = False

def set_backgrounds(back):
    print("Chnaging background to " + back)
    backfile = "/home/pi/panel_" + back +".jpg"
    subprocess.call("pcmanfm --display :0 --set-wallpaper " +backfile, shell=True)

set_backgrounds("inactive")

def video_mode():
    global video
    global burst
    if video:
       video=False
       burst = False
       print("video mode off")
       set_backgrounds("inactive")
    else:
       video=True
       burst = False
       print("video mode on")
       set_backgrounds("video")

def byebye():
    set_backgrounds("halt")
    subprocess.call("sudo nohup shutdown -h now", shell=True)

def screen_blank(mode):
    subprocess.call("xset -display :0 dpms force " + mode, shell=True)

def blank():
    global prev_active
    global camera
    if prev_active:
        camera.stop_preview()
        prev_active = False
        screen_blank("off")
    else:
        camera.start_preview(fullscreen=False,window=(0,10,580,480))
        screen_blank("on")
        prev_active = True

def burst_mode():
    global burst
    global video
    if burst:
       burst = False
       video = False
       set_backgrounds("inactive")
       print("burst mode off")
    else:
       burst=True
       video = False
       print("burst mode on")
       set_backgrounds("burst")

def take_photo():
    global video
    global camera
    global prev_active
    # Camera warm-up time
    blank()
    camera.close()
    if video:
        #time.sleep(1)
        print("taking video")
        filename = "/home/pi/Photos/img" + str(time.strftime("%Y%m%d-%H%M%S"))+".h264"
        subprocess.call(["raspivid",
                         "-t", "10000",
                         "-b", "15000000",
                         "-fps", "30",
                         "-vs",
                         "-p",
                         "0,10,580,480",
                         "-o", filename])
    else:
        if burst:
            print("taking burst")
            subprocess.call(["raspistill",
                             "-t",
                             "8500",
                             "-tl",
                             "850",
                             "-o",
                             "/home/pi/Photos/img%02d.jpg",
                             "-p",
                            "0,10,580,480",
                             "-bm",
                             "-dt"])

        else:
            print("taking still")
            filename = "/home/pi/Photos/img" + str(time.strftime("%Y%m%d-%H%M%S"))+".jpg"
            subprocess.call(["raspistill",
                             "-o",
                             filename,
                             "-ex",
                             "antishake"])
    camera = PiCamera()
    camera.rotation = 270
    blank()

b_ext.when_pressed=take_photo
b_top4.when_pressed=blank
b_2.when_pressed=video_mode
b_3.when_pressed=burst_mode
b_bot1.when_pressed=byebye
pause()
