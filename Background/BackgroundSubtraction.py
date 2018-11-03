# USAGE
# python pi_surveillance.py --conf conf.json

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from imutils.object_detection import non_max_suppression
from scipy.spatial import distance as dist
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
middle = 200

centerObjs = []
oldCenterObjs = []

avg = None
# fgbg =  cv2.bgsegm.createBackgroundSubtractorMOG()
# fgbg =  cv2.createBackgroundSubtractorMOG2()
fgbg = cv2.createBackgroundSubtractorMOG2(128,cv2.THRESH_BINARY,1)
# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	image = f.array
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy

	frame = imutils.resize(image, width=500)
	fgmask = fgbg.apply(frame)
	fgmask[fgmask==127]=0
	cv2.imshow('Mask',fgmask)

	# threshold the delta image, dilate the thresholded image to fill
	# in holes, then find contours on thresholded image
	# thresh = cv2.threshold(fgmask, 5, 255, cv2.THRESH_BINARY)[1]

	kernel = np.ones((5,5), np.uint8)


	opening = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
	cv2.imshow('Opening',opening)
	closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
	cv2.imshow('Closing',closing)

	# thresh = cv2.erode(thresh, kernel, iterations=3)
	# cv2.imshow('Erode',thresh)


	# thresh = cv2.dilate(thresh, None, iterations=2)
	# cv2.imshow('Dilate',thresh)

	
	cnts = cv2.findContours(closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		print(str(cv2.contourArea(c)))
		if cv2.contourArea(c) < 5000:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		centerObj = (int(x + w/2), y + h/2)
		centerObjs.append(centerObj)
	
	matches =	[]
	i = 0
	for centerObj in centerObjs:
		D = 1000 # high distance
		j = 0
		for oldCenterObj in oldCenterObjs:
			print("CenterX: " + str(centerObj[0]) + " OldCenterX: " + str(oldCenterObj[0]))
			print("CenterY: " + str(centerObj[1]) + " OldCenterY: " + str(oldCenterObj[1]))
			print(str(centerObj))
			print(str(oldCenterObj))
			print(str(np.array(centerObj)))
			print(str(np.array(oldCenterObj)))
			print(str(np.array([4, 0])))
			print(str(np.array([0, 3])))

			tempE = dist.euclidean(centerObj, oldCenterObj)
			tempD = dist.cdist(np.array(centerObj), np.array(oldCenterObj), 'euclidean')
			if tempD < D: 
				D = tempD
				matches[i] = (centerObj, oldCenterObj)
				matches[i] = (centerObj, oldCenterObj)
		i = i+1

	for match in matches:
		centerX = match[0][0]
		oldCenterX = match[1][0]
		print("CenterX: " + str(centerX) + " OldCenterX: " + str(oldCenterX))
		if int(centerX > middle and oldCenterX <= middle):
			print("Count")
		elif int(centerX < middle and oldCenterX >= middle):
			print("Count minus")

	oldCenterObjs = centerObjs
		

	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if totalFrames % 5 == 0:
		print("Total frames: " + str(totalFrames))
	totalFrames += 1

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)