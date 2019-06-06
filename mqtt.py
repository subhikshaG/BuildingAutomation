
# Import standard python modules.
import sys
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
# Import Adafruit IO MQTT client.
from Adafruit_IO import MQTTClient
import cv2
import requests
import json
from gpiozero import LightSensor
import time
import facecl1



# Set to Adafruit IO key & username below.
ADAFRUIT_IO_KEY      = '????' #replace ???? with adafruit key
ADAFRUIT_IO_USERNAME = '????' #replace ???? with username

# Set to the ID of the feed to subscribe to for updates.
FEED_ID1 = 'lights'
FEED_ID2='fan'
FEED_ID3='cooler'
FEED_ID4='technique'

GPIO.setmode(GPIO.BCM) # BCM numbering
#GPIO.setup(24, GPIO.OUT, initial=GPIO.LOW) # Set pin 8 to be an output pin and set initial value to low (off)
GPIO.setup(17, GPIO.OUT) #light
GPIO.setup(23, GPIO.OUT) #AC
GPIO.setup(24, GPIO.OUT) #Fan


# Define callback functions which will be called when certain events happen.
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client to make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID1))
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID2))
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID3))
    print('Connected to Adafruit IO!  Listening for {0} changes...'.format(FEED_ID4))
    # Subscribe to changes on a feed
    client.subscribe(FEED_ID1)
    client.subscribe(FEED_ID2)
    client.subscribe(FEED_ID3)
    client.subscribe(FEED_ID4)

def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

def message(client, feed_id, payload):
    # Message function will be called when a subscribed feed has a new value.
    # The feed_id parameter identifies the feed, and the payload parameter has
    # the new value.
    print('Feed {0} received new value: {1}'.format(feed_id, payload))

    if feed_id=='technique' and payload=='AUTO':
        facecl1.facedetect()# control through face detection

    if feed_id=='lights' and payload=='ON':
        GPIO.output(17, GPIO.HIGH) # Turn on the lights

    elif feed_id=='lights' and payload=='OFF':
        GPIO.output(17, GPIO.LOW) # Turn off the lights

    if feed_id=='fan' and payload=='ON':
        GPIO.output(24, GPIO.HIGH) # Turn on the fan

    elif feed_id=='fan' and payload=='OFF':
        GPIO.output(24, GPIO.LOW) # Turn off the fan

    if feed_id=='cooler' and payload=='ON':
        GPIO.output(23, GPIO.HIGH) # Turn on the cooler

    elif feed_id=='cooler' and payload=='OFF':
        GPIO.output(23, GPIO.LOW) # Turn off the cooler



# Create an MQTT client instance.
client = MQTTClient(ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_blocking()
