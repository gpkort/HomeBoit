import cv2
import time 

 
face_cascade = cv2.CascadeClassifier('haarcascade_frontalcatface.xml') 


# capture frames from a camera 
cap = cv2.VideoCapture(1) 

if not cap.isOpened():
	print("Camera is not opened")
	exit()
else:
	print("Camera is opened")


# loop runs if capturing has been initialized. 
while True:
	ret, img = cap.read()
	if not ret:
		print("Camera is not working")
		break

	# convert to gray scale of each frames 
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

	# Detects faces of different sizes in the input image 
	faces = face_cascade.detectMultiScale(gray, 1.3, 5) 

	for (x,y,w,h) in faces: 
		# To draw a rectangle in a face 
		cv2.rectangle(img,(x,y),(x+w,y+h),(255,255,0),2) 
		roi_gray = gray[y:y+h, x:x+w] 
		roi_color = img[y:y+h, x:x+w] 

	print("Number of faces found {}".format(len(faces)))
	time.sleep(2.0)

	

# Close the window 
cap.release() 


