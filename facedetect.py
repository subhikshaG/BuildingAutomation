import cv2
import sys
import RPi.GPIO as GPIO
import requests
import json
from gpiozero import LightSensor
import time
from Adafruit_IO import Client,Feed


def facedetect():
	#getting latitude and logitude
	send_url = "http://api.ipstack.com/check?access_key=????" #replace ???? with ipstack key
	geo_req = requests.get(send_url)
	geo_json = json.loads(geo_req.text)
	latitude = geo_json['latitude']
	longitude = geo_json['longitude']
	city1 = geo_json['city']

	#getting the temperature based on the latiude and logitude
	api_address='http://api.openweathermap.org/data/2.5/weather?appid=????&units=metric&lat=' #replace ???? with openweathermap api key
	long='&lon='
	url = api_address + str(latitude) + long + str(longitude)
	json_data = requests.get(url).json()
	temperaturelola = json_data['main']['temp']

	#find ambient light
	ldr = LightSensor(4)
	sum=0
	for i in range(0,10):
	        lightval=ldr.value

	        sum+=lightval

	        time.sleep(.500)
	ambientlight=sum/10

	#initialize client
	#initiate the feeds in adafruitIO
	#Adafruit is the cloud storage
	ADAFRUIT_IO_KEY = '????' #replace ???? with adafruit key
	ADAFRUIT_IO_USERNAME = '????' #replace ???? with adafruit username

	aio = Client(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

	light_feed = aio.feeds('light')
	temperature_feed = aio.feeds('temperature')
	lightbulb_feed = aio.feeds('lights')
	fan_feed = aio.feeds('fan')
	cooler_feed = aio.feeds('cooler')


	#printing values in terminal
	print ('Current longitude:=',longitude)
	print('Current latitude:=',latitude)
	print('City:=',city1)

	print('temperature',temperaturelola,'C')

	print('ambient light is ',ambientlight)

	# Get user supplied values
	imagePath = '/home/pi/training-data/student.jpg' #provide the location of the image
	cascPath = '/home/pi/opencv-3.3.0/data/haarcascades/haarcascade_frontalface_default.xml' #provide the location of the xml file

	# For each person, one face id
	face_id = 7

	# Initialize sample face image
	count = 0

	# Create the haar cascade
	faceCascade = cv2.CascadeClassifier(cascPath)

	# Read the image
	image = cv2.imread(imagePath)
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Detect faces in the image
	faces = faceCascade.detectMultiScale(
		gray,
		scaleFactor=1.1,
		minNeighbors=5,
		minSize=(30, 30),
	    #flags = cv2.cv.CV_HAAR_SCALE_IMAGE
	)

	print("Found {0} faces!".format(len(faces)))

	# Draw a rectangle around the faces
	for (x, y, w, h) in faces:
		cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
	        # Increment sample face image
		count += 1

	        # Save the captured image into the datasets folder
		cv2.imwrite(str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

	        # Display the video frame, with bounded rectangle on the person's face
		cv2.imshow('frame', image)

	#move ambient lighting and temperature to cloud
	lightz=ambientlight
	temp=temperaturelola
	aio.send(light_feed.key, str(lightz))
	aio.send(temperature_feed.key, str(temp))

	if count > 0:

		#turn on and off the necessary appliances if the face has been detected

		if ambientlight < 0.6:
			#lights on
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(17,GPIO.OUT)
			GPIO.output(17,True)
			aio.send(lightbulb_feed.key, str('ON'))

		else:
			#lightsoff
	                GPIO.setmode(GPIO.BCM)
	                GPIO.setup(17,GPIO.OUT)
	                GPIO.output(17,False)
	                aio.send(lightbulb_feed.key, str('OFF'))


		if temperaturelola > 35.00:
			#AC on,fan off
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(23,GPIO.OUT)
			GPIO.output(23,True)
			aio.send(cooler_feed.key, str('ON'))

			GPIO.setup(24,GPIO.OUT)
			GPIO.output(24,False)
			aio.send(fan_feed.key, str('OFF'))

		elif temperaturelola > 25.00:
			#AC off,fan On
	                GPIO.setmode(GPIO.BCM)
	                GPIO.setup(24,GPIO.OUT)
	                GPIO.output(24,True)
	                aio.send(fan_feed.key, str('ON'))

	                GPIO.setup(23,GPIO.OUT)
	                GPIO.output(23,False)
	                aio.send(cooler_feed.key, str('OFF'))


		else:
			#ac and fan off
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(23,GPIO.OUT)
			GPIO.output(23,False)
			aio.send(cooler_feed.key, str('OFF'))

			GPIO.setup(24,GPIO.OUT)
			GPIO.output(24,False)
			aio.send(fan_feed.key, str('OFF'))

	else:
		#switch off all the devices since face has not been detected

	        GPIO.setmode(GPIO.BCM)
	        GPIO.setup(17,GPIO.OUT)
	        GPIO.output(17,False)
	        aio.send(lightbulb_feed.key, str('OFF'))

	        GPIO.setup(23,GPIO.OUT)
	        GPIO.output(23,False)
	        aio.send(cooler_feed.key, str('OFF'))

	        GPIO.setup(24,GPIO.OUT)
	        GPIO.output(24,False)
	        aio.send(fan_feed.key, str('OFF'))

	cv2.imshow("Faces found", image)
	cv2.waitKey(0)
