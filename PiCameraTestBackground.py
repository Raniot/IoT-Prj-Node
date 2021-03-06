# USAGE
# python pi_surveillance.py --conf conf.json

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils.object_detection import non_max_suppression
import numpy as np
import argparse
import warnings
import datetime
import imutils
import dlib
import json
import time
import cv2

warnings.filterwarnings("ignore")

camera = PiCamera()
camera.resolution = [640, 480]
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=[640, 480])

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(2.5)
totalFrames = 0
skip_frames = 40

avg = None

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	image = f.array
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy

	frame = imutils.resize(image, width=500)

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (21, 21), 0)

	if avg is None:
		print("[INFO] starting background model...")
		avg = gray.copy().astype("float")
		rawCapture.truncate(0)
		continue

	cv2.accumulateWeighted(gray, avg, 0.5)

	if totalFrames % skip_frames == 0:
		frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

		# threshold the delta image, dilate the thresholded image to fill
		# in holes, then find contours on thresholded image
		thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
		thresh = cv2.dilate(thresh, None, iterations=2)
		cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		cnts = cnts[0] if imutils.is_cv2() else cnts[1]

		# loop over the contours
		for c in cnts:
			# if the contour is too small, ignore it
			if cv2.contourArea(c) < 5000:
				continue

			# compute the bounding box for the contour, draw it on the frame,
			# and update the text
			(x, y, w, h) = cv2.boundingRect(c)
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
			print("Detected")

		cv2.imshow("Frame", frame)
		cv2.imshow("frameDelta", frameDelta)
		cv2.imshow("thresh", thresh)

	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if totalFrames % 5 == 0:
		print("Total frames: " + str(totalFrames))
	totalFrames += 1

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)