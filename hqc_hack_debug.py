"""Debug version"""
from gpiozero import Button
from picamera import PiCamera
from signal import pause
import subprocess
import time
import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logging.debug("Starting")
BACKDIR = "/home/pi/HQC-case-hack/images"
DATADIR = "/home/pi/Pictures"
# Adafruit TFT buttons
b_bot1 = Button(27)
b_top4 = Button(17)
b_2 = Button(22)
b_3 = Button(23)
# External button on GPIO 12
b_ext = Button(12)

# operation modea
video = False
burst = False

logging.debug("connecting to camera")
camera = PiCamera()
# Limit preview window size to reveal button labels on screen background
camera.start_preview(fullscreen=False, window=(0, 10, 580, 480))
prev_active = True

def set_backgrounds(back):
    """Calls the pcmanfm command to change the desktop wallpaper."""
    logging.debug("Changing background to " + back)
    bfile = BACKDIR + "/panel_" + back + ".jpg"
    subprocess.call("pcmanfm --display :0 --set-wallpaper " + bfile, shell = True)

set_backgrounds("inactive")

def video_mode():
    """Run when a button is pressed: sets the mode to video"""
    global video
    global burst
    if video:
        video = False
        burst = False
        ("video mode off")
        set_backgrounds("inactive")
    else:
        video = True
        burst = False
        logging.debug("video mode on")
        set_backgrounds("video")

def byebye():
    """Run when a button is pressed: Shuts down the Raspberry Pi"""
    set_backgrounds("halt")
    logging.debug("halting")
    subprocess.call("sudo nohup shutdown -h now", shell=True)

def blank():
    """Run when a button is pressed: Blanks/unblanks the screen"""
    global prev_active
    global camera
    if prev_active:
        logging.debug("blanking")
        camera.stop_preview()
        prev_active = False
        subprocess.call("xset -display :0 dpms force off", shell=True)
    else:
        logging.debug("un-blanking")
        camera.start_preview(fullscreen=False, window=(0, 10, 580, 480))
        subprocess.call("xset -display :0 dpms force on", shell=True)
        prev_active = True

def burst_mode():
    """Run when a button is pressed: sets the mode to burst"""
    global burst
    global video
    if burst:
        burst = False
        video = False
        set_backgrounds("inactive")
        logging.debug("burst mode off")
    else:
        burst = True
        video = False
        logging.debug("burst mode on")
        set_backgrounds("burst")

def take_photo():
    """Run when a button is pressed: Captures data based on operation mode"""
    global camera
    global prev_active
    blank()
    camera.close()  # Closes PiCamera connection
    if video:  # take a 10 second video
        logging.debug("starting video")
        filename = DATADIR + "/vid" + str(time.strftime("%Y%m%d-%H%M%S"))+".h264"
        subprocess.call(["raspivid",
                         "-t", "10000",
                         "-b", "15000000",
                         "-fps", "30",
                         "-vs",
                         "-p", "0,10,580,480",
                         "-o", filename])
        logging.debug("finished video")
    else:
        if burst:  # Take 10 rapid still images
            logging.debug("taking burst")
            subprocess.call(["raspistill",
                             "-t", "8500",
                             "-tl", "850",
                             "-o", DATADIR + "/img%02d.jpg",
                             "-p", "0,10,580,480",
                             "-bm",
                             "-dt"])
            logging.debug("finished burst")

        else:  # Take a single still image
            logging.debug("taking still")
            filename = DATADIR + "/img" + str(time.strftime("%Y%m%d-%H%M%S"))+".jpg"
            subprocess.call(["raspistill",
                             "-o", filename,
                             "-p", "0,10,580,480",
                             "-ex", "antishake"])
    camera = PiCamera()  # re-connect to Camera using PiCamera
    blank()

# Set functions to be run when buttons pressed
b_ext.when_pressed = take_photo
b_top4.when_pressed = blank
b_2.when_pressed = video_mode
b_3.when_pressed = burst_mode
b_bot1.when_pressed = byebye
pause()  # Keep the program active
