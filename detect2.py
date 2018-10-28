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
import imutils
import cv2


# initialize the HOG descriptor/person detector
hog = cv2.HOGDescriptor()
hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

framerate=10
resolution = (640, 480)

totalFrames = 0
skip_frames = 40
# initialize the picamera stream and allow the camera
# sensor to warmup
stream = PiVideoStream(resolution=resolution, 	framerate=framerate).start()
time.sleep(2.0)
vs = stream
fullbody_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
# loop over frames from the video stream
while True:

    if totalFrames % skip_frames == 0:
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

        # show the output images
        # cv2.imshow("Before NMS", orig)
        cv2.imshow("Frame", image)
        cv2.waitKey(0)
    totalFrames += 1