# import the necessary packages
import argparse
import datetime
import json
import sys
import time
import warnings

import cv2
import dlib
import imutils
import numpy as np
from imutils.object_detection import non_max_suppression
from picamera import PiCamera
from picamera.array import PiRGBArray
from scipy.spatial import distance as dist


def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", "--verbose", help="Enable Verbose", type=bool, default=False)
	# Parse arguments
	args = parser.parse_args()

	return args

# get arguments
args = parseArguments()
VERBOSE = args.verbose

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
enterArea = 0
leaveArea = 0

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
	

	# # Find matches between objects and the obejcts observed in previous frame. 
	# matches = dict()
	# i = 0
	# for centerObj in centerObjs:
	# 	D = 1000 # high distance
	# 	j = 0
	# 	for oldCenterObj in oldCenterObjs:
	# 		if VERBOSE: print("Center: " + str(centerObj) + "OldCenter: " + str(oldCenterObj))
	# 		tempD = dist.euclidean(centerObj, oldCenterObj)
	# 		if tempD < D: 
	# 			D = tempD
	# 			matches[str(i)] = (centerObj, oldCenterObj)
	# 	i = i+1

	# Find matches between objects and the obejcts observed in previous frame. 
	matches = dict()
	i = 0

	if len(oldCenterObjs) != 0:


		# test = np.array([[0.59, 1.23], [0.89, 1.67], [0.21,0.99]])
		# D = dist.cdist(test, test)
		
		D = dist.cdist(np.array(oldCenterObjs), np.array(centerObjs))
		rows = D.min(axis=1).argsort()
		cols = D.argmin(axis=1)[rows]
		usedRows = set()
		usedCols = set()

		for (row, col) in zip(rows, cols):
				# if we have already examined either the row or
				# column value before, ignore it
				if row in usedRows or col in usedCols:
					continue

				# if the distance between centroids is greater than
				# the maximum distance, do not associate the two
				# centroids to the same object
				maxDistance = 200
				if D[row, col] > maxDistance:
					continue

				
				
				centerX = centerObjs[col][0]
				oldCenterX = oldCenterObjs[row][0]
				if int(centerX > halfWidthAfterScale and oldCenterX <= halfWidthAfterScale):
					print("1")
					sys.stdout.flush()
					enterArea = enterArea + 1
				elif int(centerX < halfWidthAfterScale and oldCenterX >= halfWidthAfterScale):
					print("-1")
					sys.stdout.flush()
					leaveArea = leaveArea + 1

				# indicate that we have examined each of the row and
				# column indexes, respectively
				usedRows.add(row)
				usedCols.add(col)


		# compute both the row and column index we have NOT yet
		# examined
		unusedRows = set(range(0, D.shape[0])).difference(usedRows)
		unusedCols = set(range(0, D.shape[1])).difference(usedCols)

		# in the event that the number of object centroids is
		# equal or greater than the number of input centroids
		# we need to check and see if some of these objects have
		# potentially disappeared
		# if D.shape[0] >= D.shape[1]:
			# loop over the unused row indexes
			# for row in unusedRows:
				# grab the object ID for the corresponding row
				# index and increment the disappeared counter
			# objectID = objectIDs[row]
			# self.disappeared[objectID] += 1

				# check to see if the number of consecutive
				# frames the object has been marked "disappeared"
				# for warrants deregistering the object
			# if self.disappeared[objectID] > self.maxDisappeared:
			# 	self.deregister(objectID)

		# otherwise, if the number of input centroids is greater
		# than the number of existing object centroids we need to
		# register each new input centroid as a trackable object
		# else:
		# 	for col in unusedCols:
			# self.register(inputCentroids[col])


		# See if the object has crossed the middle from the last frame to the current frame
		# for key, value in matches.items():
		# 	centerX = value[0][0]
		# 	oldCenterX = value[1][0]
		# 	if VERBOSE: print("CenterX: " + str(centerX) + " OldCenterX: " + str(oldCenterX))
		# 	if int(centerX > halfWidthAfterScale and oldCenterX <= halfWidthAfterScale):
		# 		print("1")
		# 		sys.stdout.flush()
		# 		enterArea = enterArea + 1
		# 	elif int(centerX < halfWidthAfterScale and oldCenterX >= halfWidthAfterScale):
		# 		print("-1")
		# 		sys.stdout.flush()
		# 		leaveArea = leaveArea + 1

	oldCenterObjs = centerObjs.copy()

	# construct a tuple of information to be displayed
	info = [
		("Enter Area", enterArea),
		("Leave Area", leaveArea),
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
