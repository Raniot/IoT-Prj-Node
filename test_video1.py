# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import datetime
import imutils
import cv2
 
# initialize the camera and grab a reference to the raw camera capture
# camera = PiCamera()
# camera.resolution = (640, 480)
# camera.framerate = 32
# rawCapture = PiRGBArray(camera, size=(640, 480))

# initialize the frame dimensions (we'll set them as soon as we read
# the first frame from the video)
W = 640
H = 480
 
# allow the camera to warmup
#time.sleep(0.1)

from imutils.video.pivideostream import PiVideoStream
framerate=32
resolution = (640, 480)
# initialize the picamera stream and allow the camera
# sensor to warmup
stream = PiVideoStream(resolution=resolution, 	framerate=framerate).start()
time.sleep(2.0)
vs = stream
# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	frame = imutils.resize(frame, width=400)
 
	# draw the timestamp on the frame
	timestamp = datetime.datetime.now()
	ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
	cv2.putText(frame, ts, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
		0.35, (0, 0, 255), 1)
 
	# show the frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
 
# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
 
# # capture frames from the camera
# for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
# 	# grab the raw NumPy array representing the image, then initialize the timestamp
# 	# and occupied/unoccupied text
# 	image = frame.array
 
# 	# show the frame

# 	cv2.line(frame, (0, H // 2), (W, H // 2), (0, 255, 255), 2)
# 	cv2.imshow("Frame", image)
# 	key = cv2.waitKey(1) & 0xFF
 
# 	# clear the stream in preparation for the next frame
# 	rawCapture.truncate(0)
 
# 	# if the `q` key was pressed, break from the loop
# 	if key == ord("q"):
# 		break