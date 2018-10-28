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


# initialize the video writer (we'll instantiate later if need be)
writer = None

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
W = None
H = None

# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers, followed by a dictionary to
# map each unique object ID to a TrackableObject
#ct = CentroidTracker(maxDisappeared=40, maxDistance=50)
trackers = []
trackableObjects = {}

# initialize the total number of frames processed thus far, along
# with the total number of objects that have moved either up or down
totalFrames = 0
skip_frames = 120
#totalDown = 0
#totalUp = 0

# start the frames per second throughput estimator
fps = FPS().start()

#avg = None

# loop over frames from the video stream
while True:

    status = "Waiting"
    rects = []

	# check to see if we should run a more computationally expensive
	# object detection method to aid our tracker
    if totalFrames % skip_frames == 0:
        # set the status and initialize our new set of object trackers
        print("Detecting")
        status = "Detecting"
        trackers = []

        frame = vs.read()

		
        if W is None or H is None:
            (H, W) = frame.shape[:2]
	    # resize the frame, convert it to grayscale, and blur it

        # face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        fullbody_cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')
        # eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        # img = cv.imread('sachin.jpg')
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        fullbodies = fullbody_cascade.detectMultiScale(gray, 1.1, 3, None)
        for (x,y,w,h) in fullbodies:
            print("Body Found at xStart:" + str(x) + " yStart: " + str(y) + " xEnd: "+ str(x+w) + " yEnd: " + str(y+h))
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
            # roi_gray = gray[y:y+h, x:x+w]
            # roi_color = img[y:y+h, x:x+w]

            # construct a dlib rectangle object from the bounding
			# box coordinates and then start the dlib correlation
			# tracker
            tracker = dlib.correlation_tracker()
            rect = dlib.rectangle(x, y, x+w, y+h)
            tracker.start_track(gray, rect)

			# add the tracker to our list of trackers so we can
			# utilize it during skip frames
            trackers.append(tracker)

	# otherwise, we should utilize our object *trackers* rather than
	# object *detectors* to obtain a higher frame processing throughput
    else:
		# loop over the trackers
        for tracker in trackers:
			# set the status of our system to be 'tracking' rather
			# than 'waiting' or 'detecting'
            status = "Tracking"

			# update the tracker and grab the updated position
            tracker.update(gray)
            pos = tracker.get_position()

			# unpack the position object
            startX = int(pos.left())
            startY = int(pos.top())
            endX = int(pos.right())
            endY = int(pos.bottom())

			# add the bounding box coordinates to the rectangles list
            rects.append((startX, startY, endX, endY))
            cv2.rectangle(frame,(startX,startY),(endX,endY),(255,0,0),2)

	# draw a horizontal line in the center of the frame -- once an
	# object crosses this line we will determine whether they were
	# moving 'up' or 'down'

    # cv2.line(frame, (0, H // 2), (W, H // 2), (0, 255, 255), 2)

	# use the centroid tracker to associate the (1) old object
	# centroids with (2) the newly computed object centroids
	# objects = ct.update(rects)

	# # loop over the tracked objects
	# for (objectID, centroid) in objects.items():
	# 	# check to see if a trackable object exists for the current
	# 	# object ID
	# 	to = trackableObjects.get(objectID, None)

	# 	# if there is no existing trackable object, create one
	# 	if to is None:
	# 		to = TrackableObject(objectID, centroid)

	# 	# otherwise, there is a trackable object so we can utilize it
	# 	# to determine direction
	# 	else:
	# 		# the difference between the y-coordinate of the *current*
	# 		# centroid and the mean of *previous* centroids will tell
	# 		# us in which direction the object is moving (negative for
	# 		# 'up' and positive for 'down')
	# 		y = [c[1] for c in to.centroids]
	# 		direction = centroid[1] - np.mean(y)
	# 		to.centroids.append(centroid)

	# 		# check to see if the object has been counted or not
	# 		if not to.counted:
	# 			# if the direction is negative (indicating the object
	# 			# is moving up) AND the centroid is above the center
	# 			# line, count the object
	# 			if direction < 0 and centroid[1] < H // 2:
	# 				totalUp += 1
	# 				to.counted = True

	# 			# if the direction is positive (indicating the object
	# 			# is moving down) AND the centroid is below the
	# 			# center line, count the object
	# 			elif direction > 0 and centroid[1] > H // 2:
	# 				totalDown += 1
	# 				to.counted = True

	# 	# store the trackable object in our dictionary
	# 	trackableObjects[objectID] = to

	# 	# draw both the ID of the object and the centroid of the
	# 	# object on the output frame
	# 	text = "ID {}".format(objectID)
	# 	cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
	# 		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	# 	cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

	# construct a tuple of information we will be displaying on the
	# frame
    info = [
		# ("Up", totalUp),
		# ("Down", totalDown),
		("Status", status),
		("Total Frames", str(totalFrames)),
	]

	# loop over the info tuples and draw them on our frame
    for (i, (k, v)) in enumerate(info):
        text = "{}: {}".format(k, v)
        cv2.putText(frame, text, (10, H - ((i * 20) + 20)),
			cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

	# check to see if we should write the frame to disk
	# if writer is not None:
	# 	writer.write(frame)

	# show the output frame
    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

	# if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

	# increment the total number of frames processed thus far and
	# then update the FPS counter
    totalFrames += 1
    fps.update()
    if(totalFrames % 5 == 0):
        print("Total Frames : " + str(totalFrames))

# stop the timer and display FPS information
fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# check to see if we need to release the video writer pointer
# if writer is not None:
# 	writer.release()

# if we are not using a video file, stop the camera video stream
# if not args.get("input", False):
vs.stop()

# otherwise, release the video file pointer
# else:
	# vs.release()

# close any open windows
cv2.destroyAllWindows()