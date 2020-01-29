import platform
import time
import os
from datetime import datetime
from PIL import Image
from flask import current_app as app

if (platform.platform()[0:7] != 'Windows') :
    import picamera as picamera
else:
    from .picamearaemul import picamera as picamera

def takePicture():
    with picamera.PiCamera() as camera:
        camera.resolution = (2592, 1944)
        camera.start_preview()
        time.sleep(2)
        theorigpath = os.path.join(app.root_path, 'campics')
        filenamefromtime = time.strftime("%Y%m%d-%H%M%S")
        filenamethumb = filenamefromtime + "_thn.jpg"
        filenamefromtime = filenamefromtime + ".jpg"
        thepath = os.path.join(theorigpath, filenamefromtime)
        camera.capture(thepath)
        thePicture = Image.open(thepath)
        thePicture.thumbnail((80, 60))
        thepath = os.path.join(theorigpath, filenamethumb)
        thePicture.save(thepath)

def deleteSinglePictureShared(path):
    filename = os.path.join(app.root_path, 'campics')
    filename = os.path.join(filename, path)
    filenamethumb, file_extension = os.path.splitext(filename)
    filenamethumb = filenamethumb + "_thn.jpg"
    os.remove(filename)
    os.remove(filenamethumb)
