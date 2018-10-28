# USAGE
# To read and write back out to video:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel --input videos/example_01.mp4 \
#	--output output/output_01.avi
#
# To read from webcam and write back out to disk:
# python people_counter.py --prototxt mobilenet_ssd/MobileNetSSD_deploy.prototxt \
#	--model mobilenet_ssd/MobileNetSSD_deploy.caffemodel \
#	--output output/webcam_output.avi

# import the necessary packages
from imutils.video import VideoStream
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
import numpy as np
import imutils
import time
import dlib
import cv2


# if a video path was not supplied, grab a reference to the webcam
# if not args.get("input", False):
	# print("[INFO] starting video stream...")
	# vs = VideoStream(src=0).start()
	# time.sleep(2.0)

# # otherwise, grab a reference to the video file
# else:
	# print("[INFO] opening video file...")
	# vs = cv2.VideoCapture(args["input"])

framerate=10
resolution = (640, 480)
# initialize the picamera stream and allow the camera
# sensor to warmup
stream = PiVideoStream(resolution=resolution, 	framerate=framerate).start()
time.sleep(2.0)
vs = stream
fullbody_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
# loop over frames from the video stream
while True:
    frame = vs.read()
    frame=imutils.resize(frame, width=min(100, frame.shape[1]))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    upper=fullbody_cascade.detectMultiScale(gray,1.1,1)
    #print lips
    for (a,b,c,d) in upper:
        cv2.rectangle(frame,(a,b),(a+c,b+d),(0,0,255),2)
    print(len(upper))
    cv2.imshow('detect',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

vs.release() 
cv2.destroyAllWindows()