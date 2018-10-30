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


# construct the argument parser and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-c", "--conf", required=True,
#	help="path to the JSON configuration file")
#args = vars(ap.parse_args())

# filter warnings, load the configuration and initialize the Dropbox
# client
warnings.filterwarnings("ignore")
#conf = json.load(open(args["conf"]))
#client = None

# # check to see if the Dropbox should be used
# if conf["use_dropbox"]:
# 	# connect to dropbox and start the session authorization process
# 	client = dropbox.Dropbox(conf["dropbox_access_token"])
# 	print("[SUCCESS] dropbox account linked")

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = [640, 480]
camera.framerate = 10
rawCapture = PiRGBArray(camera, size=[640, 480])

# allow the camera to warmup, then initialize the average frame, last
# uploaded timestamp, and frame motion counter
print("[INFO] warming up...")
time.sleep(2.5)
#avg = None
totalFrames = 0
skip_frames = 40

#lastUploaded = datetime.datetime.now()
#motionCounter = 0

# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
trackers = []

# capture frames from the camera
for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

	image = f.array
	# load the image and resize it to (1) reduce detection time
	# and (2) improve detection accuracy
	image = imutils.resize(image, width=min(400, image.shape[1]))
	if totalFrames % skip_frames == 0:
		print("Trying to detect")
		trackers.clear()
		# orig = image.copy()

		# detect people in the image
		(rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
			padding=(8, 8), scale=1.05)

		# draw the original bounding boxes
		# for (x, y, w, h) in rects:
		#	 cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

		# apply non-maxima suppression to the bounding boxes using a
		# fairly large overlap threshold to try to maintain overlapping
		# boxes that are still people
		rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
		pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

		# draw the final bounding boxes
		for (xA, yA, xB, yB) in pick:
			cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
			# tracker = dlib.correlation_tracker()
			tracker = cv2.TrackerBoosting_create()
			margin = 30
			# rect2 = dlib.rectangle(xA-margin, yA-margin, xB-margin, yB-margin)
			bbox = (xA+margin, yA+margin, xB-margin, yB-margin)
			tracker.init(image, bbox)
			# add the tracker to our list of trackers so we can
			# utilize it during skip frames
			trackers.append(tracker)
		
	else:
		# loop over the trackers
		for tracker in trackers:
			# set the status of our system to be 'tracking' rather
			# than 'waiting' or 'detecting'
			#status = "Tracking"

			# update the tracker and grab the updated position
			ok, bbox = tracker.update(image)
			# pos = tracker.get_position()

			if ok:
				# Tracking success
				p1 = (int(bbox[0]), int(bbox[1]))
				p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
				cv2.rectangle(image, p1, p2, (255,0,0),2)
			else :
				# Tracking failure
				print("Tracking failure detected")

			# # unpack the position object
			# startX = int(pos.left())
			# startY = int(pos.top())
			# endX = int(pos.right())
			# endY = int(pos.bottom())

			# # add the bounding box coordinates to the rectangles list
			# # rects1.append((startX, startY, endX, endY))
			# cv2.rectangle(image,(startX,startY),(endX,endY),(255,0,0),2)

	# show the output images
	# cv2.imshow("Before NMS", orig)
	cv2.imshow('Frame',image)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
	if totalFrames % 5 == 0:
		print("Total frames: " + str(totalFrames))
	totalFrames += 1

	# clear the stream in preparation for the next frame
	rawCapture.truncate(0)
