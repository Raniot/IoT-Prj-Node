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
import sys

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", help="Tell if script should verbose print", type=bool, default=False)
	# Parse arguments
	args = parser.parse_args()

	return args

args = parseArguments()

VERBOSE = args.verbose
print('Verbose: ' + str(VERBOSE))

warnings.filterwarnings("ignore")

camera = PiCamera()
width = 640
height = 480

widthAfterScale = None
heightAfterScale = None
halfWidthAfterScale = None


camera.resolution = [width, height]
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=[width, height])

# allow the camera to warmup
time.sleep(2.5)
totalFrames = 0
skip_frames = 40
enterSofa = 0
leaveSofa = 0

centerObjs = []
oldCenterObjs = []

fgbg = cv2.createBackgroundSubtractorMOG2(128,cv2.THRESH_BINARY,1)
# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	image = f.array
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy

	frame = imutils.resize(image, width=500)

	if widthAfterScale is None or heightAfterScale is None or halfWidthAfterScale is None:
		(heightAfterScale, widthAfterScale) = frame.shape[:2]
		halfWidthAfterScale = widthAfterScale/2

	fgmask = fgbg.apply(frame)
	fgmask[fgmask==127]=0

	kernel = np.ones((5,5), np.uint8)
	opening = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
	closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
	
	cnts = cv2.findContours(closing.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = cnts[0] if imutils.is_cv2() else cnts[1]

	centerObjs.clear()
	# loop over the contours
	for c in cnts:
		# if the contour is too small, ignore it
		if VERBOSE: print(str(cv2.contourArea(c)))
		if cv2.contourArea(c) < 5000:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
		centerObj = (int(x + w/2), y + h/2)
		centerObjs.append(centerObj)
	
	# matches = [None] * (int)(centerObjs.count)
	matches = dict()
	i = 0
	for centerObj in centerObjs:
		D = 1000 # high distance
		j = 0
		for oldCenterObj in oldCenterObjs:
			if VERBOSE: print("Center: " + str(centerObj) + "OldCenter: " + str(oldCenterObj))
			tempD = dist.euclidean(centerObj, oldCenterObj)
			if tempD < D: 
				D = tempD
				matches[str(i)] = (centerObj, oldCenterObj)
		i = i+1

	for key, value in matches.items():
		centerX = value[0][0]
		oldCenterX = value[1][0]
		if VERBOSE: print("CenterX: " + str(centerX) + " OldCenterX: " + str(oldCenterX))
		if int(centerX > halfWidthAfterScale and oldCenterX <= halfWidthAfterScale):
			print("1")
			sys.stdout.flush()
			enterSofa = enterSofa + 1
		elif int(centerX < halfWidthAfterScale and oldCenterX >= halfWidthAfterScale):
			print("-1")
			sys.stdout.flush()
			leaveSofa = leaveSofa + 1


	oldCenterObjs = centerObjs.copy()

	# construct a tuple of information we will be displaying on the
	# frame
	info = [
		("Enter Sofa", enterSofa),
		("Leave Sofa", leaveSofa),
	]

	# loop over the info tuples and draw them on our frame
	for (i, (k, v)) in enumerate(info):
		text = "{}: {}".format(k, v)
		cv2.putText(frame, text, (10, heightAfterScale - ((i * 20) + 20)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


	cv2.line(frame, (int(halfWidthAfterScale), 0), (int(halfWidthAfterScale), height), (0, 255, 255), 2)
	cv2.imshow('frame',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if VERBOSE: 
		if totalFrames % 50 == 0:
			print("Total frames: " + str(totalFrames))
	totalFrames += 1

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)