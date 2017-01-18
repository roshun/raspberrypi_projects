'''
/*
 * Copyright 2010-2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import sys
import logging
import time
import getopt
import subprocess
from time import gmtime, strftime

def vizio_search(message):
    # Navigate to the Netflix search screen
    # TODO: handle searching after a previous search versus searching from scratch, maybe use a different keyword?
    subprocess.Popen("irsend SEND_ONCE vizio KEY_NETFLIX",shell=True)
    time.sleep(3)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_OK",shell=True)
    time.sleep(1)
    for i in list(message):
        if i == " ":
            subprocess.Popen("irsend SEND_ONCE vizio KEY_SPACE", shell=True)
        else:
            subprocess.Popen("irsend SEND_ONCE vizio KEY_" + i.upper(), shell=True)
        time.sleep(1)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_SPACE", shell=True)
    time.sleep(1)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_DELETE", shell=True)
    time.sleep(1)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_RIGHT", shell=True)
    time.sleep(1)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_OK", shell=True)
    time.sleep(1)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_OK", shell=True)
    return True

def vizio_clear():
    subprocess.Popen("irsend SEND_START vizio KEY_LEFT", shell=True)
    time.sleep(2)
    subprocess.Popen("irsend SEND_STOP vizio KEY_LEFT", shell=True)
    time.sleep(0.5)
    subprocess.Popen("irsend SEND_START vizio KEY_DELETE", shell=True)
    time.sleep(5)
    subprocess.Popen("irsend SEND_STOP vizio KEY_DELETE", shell=True)
    return True

def vizio_open_video_service(service):
    subprocess.Popen("irsend SEND_ONCE vizio KEY_" + service, shell=True)
    time.sleep(3)
    #subprocess.Popen("irsend SEND_ONCE vizio KEY_OK", shell=True)
    return True

# Custom MQTT message callback
def customCallback(client, userdata, message):
    repetition = 1
    if message.payload.split()[0] == "search":
        vizio_search(message.payload.replace("search ",""))
    elif message.payload.split()[0] == "clear":
        vizio_clear()
    elif message.payload.split()[0] == "video_service":
        vizio_open_video_service(message.payload.upper().split()[1])
    else:
        if message.payload.upper().split()[1] == "OKAY":
            button = "KEY_OK"
        #elif message.payload.upper().split()[1] == "PAUSE":
        #    button = "KEY_PLAY"
        elif (message.payload.upper().split()[1] == "ON" or message.payload.upper().split()[1] == "OFF") and message.payload.split()[0] == "power_state":
            button = "KEY_POWER"
        elif message.payload.split()[0] == "volume":
            if message.payload.upper().split()[1] == "UP":
                button = "KEY_VOLUMEUP"
                repetition = int(message.payload.split()[2])
                print "Turning volume up by %s" % repetition
            elif message.payload.upper().split()[1] == "DOWN":
                button = "KEY_VOLUMEDOWN"
                repetition = int(message.payload.split()[2])
                print "Turning volume down by %s" % repetition
            # TODO: build in some error handling here for incorrect volume settings
        else:
            button = "KEY_" + message.payload.upper().split()[1]
        for i in range(repetition):
            subprocess.Popen("irsend SEND_ONCE vizio " + button, shell=True)
            time.sleep(0.3)
    
    with open("/home/pi/alexa_remote_commands_vizio.log", "a") as myfile:
        myfile.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) +  "\t" + message.topic + "\t" + message.payload + "\n")

    #print("Received a new message: ")
    #print(message.payload)
    #print("from topic: ")
    #print(message.topic)
    #print("--------------\n\n")

# Usage
usageInfo = """Usage:

Use certificate based mutual authentication:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

Use MQTT over WebSocket:
python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -w

Type "python basicPubSub.py -h" for available options.
"""
# Help info
helpInfo = """-e, --endpoint
	Your AWS IoT custom endpoint
-r, --rootCA
	Root CA file path
-c, --cert
	Certificate file path
-k, --key
	Private key file path
-w, --websocket
	Use MQTT over WebSocket
-h, --help
	Help information


"""

# Read in command-line parameters
useWebsocket = False
host = ""
rootCAPath = ""
certificatePath = ""
privateKeyPath = ""
try:
	opts, args = getopt.getopt(sys.argv[1:], "hwe:k:c:r:", ["help", "endpoint=", "key=","cert=","rootCA=", "websocket"])
	if len(opts) == 0:
		raise getopt.GetoptError("No input parameters!")
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print(helpInfo)
			exit(0)
		if opt in ("-e", "--endpoint"):
			host = arg
		if opt in ("-r", "--rootCA"):
			rootCAPath = arg
		if opt in ("-c", "--cert"):
			certificatePath = arg
		if opt in ("-k", "--key"):
			privateKeyPath = arg
		if opt in ("-w", "--websocket"):
			useWebsocket = True
except getopt.GetoptError:
	print(usageInfo)
	exit(1)

# Missing configuration notification
missingConfiguration = False
if not host:
	print("Missing '-e' or '--endpoint'")
	missingConfiguration = True
if not rootCAPath:
	print("Missing '-r' or '--rootCA'")
	missingConfiguration = True
if not useWebsocket:
	if not certificatePath:
		print("Missing '-c' or '--cert'")
		missingConfiguration = True
	if not privateKeyPath:
		print("Missing '-k' or '--key'")
		missingConfiguration = True
if missingConfiguration:
	exit(2)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicSub", useWebsocket=True)
	myAWSIoTMQTTClient.configureEndpoint(host, 443)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
	myAWSIoTMQTTClient = AWSIoTMQTTClient("basicSub")
	myAWSIoTMQTTClient.configureEndpoint(host, 8883)
	myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, customCallback)
time.sleep(2)

## Publish to the same topic in a loop forever
loopCount = 0
while True:
#	myAWSIoTMQTTClient.publish("things/RaspberryPi/shadow", "New Message " + str(loopCount), 1)
	loopCount += 1
	time.sleep(1)
