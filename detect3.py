# USAGE
# python detect.py --images images

# import the necessary packages
from __future__ import print_function
from imutils.object_detection import non_max_suppression
from imutils.video import VideoStream
from imutils.video.pivideostream import PiVideoStream
from imutils import paths
import numpy as np
import time
import dlib
import imutils
import cv2


# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

framerate=10
resolution = (640, 480)

trackers = []

totalFrames = 0
skip_frames = 240
# initialize the picamera stream and allow the camera
# sensor to warmup
stream = PiVideoStream(resolution=resolution, 	framerate=framerate).start()
time.sleep(2.0)
vs = stream
fullbody_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
# loop over frames from the video stream
while True:

    if totalFrames % skip_frames == 0:
        print("Trting to detect")
        # load the image and resize it to (1) reduce detection time
        # and (2) improve detection accuracy
        image = vs.read()
        image = imutils.resize(image, width=min(400, image.shape[1]))
        # orig = image.copy()

        # detect people in the image
        (rects, weights) = hog.detectMultiScale(image, winStride=(4, 4),
            padding=(8, 8), scale=1.05)

        # draw the original bounding boxes
        # for (x, y, w, h) in rects:
        #     cv2.rectangle(orig, (x, y), (x + w, y + h), (0, 0, 255), 2)

        # apply non-maxima suppression to the bounding boxes using a
        # fairly large overlap threshold to try to maintain overlapping
        # boxes that are still people
        rects = np.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        pick = non_max_suppression(rects, probs=None, overlapThresh=0.65)

        # draw the final bounding boxes
        for (xA, yA, xB, yB) in pick:
            cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
            tracker = dlib.correlation_tracker()
            rect = dlib.rectangle(xA, yA, xB, yB)
            tracker.start_track(image, rect)
            trackers.append(tracker)

        # show the output images
        # cv2.imshow("Before NMS", orig)
        cv2.imshow('Frame',image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # add the tracker to our list of trackers so we can
        # utilize it during skip frames
        trackers.append(tracker)
    else:
		# loop over the trackers
        for tracker in trackers:
			# set the status of our system to be 'tracking' rather
			# than 'waiting' or 'detecting'
            status = "Tracking"

			# update the tracker and grab the updated position
            tracker.update(image)
            pos = tracker.get_position()

			# unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

			# add the bounding box coordinates to the rectangles list
            rects.append((startX, startY, endX, endY))
            cv2.rectangle(image,(startX,startY),(endX,endY),(255,0,0),2)

    if totalFrames % 5 == 0:
        print("Total frames: " + str(totalFrames))
    totalFrames += 1

vs.release()
cv2.destroyAllWindows()