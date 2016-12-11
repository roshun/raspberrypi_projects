import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import random

myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")

def lambda_handler(event, context):
    
    mqttSetup(myAWSIoTMQTTClient)
    
    if (event["session"]["application"]["applicationId"] !=
            "amzn1.ask.skill.197427b8-71b0-45bb-a9ce-ff4488db467d"):
        raise ValueError("Invalid Application ID")
    
    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event["request"]["type"] == "LaunchRequest":
        return on_launch(event["request"], event["session"])
    elif event["request"]["type"] == "IntentRequest":
        return on_intent(event["request"], event["session"])
    elif event["request"]["type"] == "SessionEndedRequest":
        return on_session_ended(event["request"], event["session"])

def mqttSetup(MQTTClient):
    
    # MQTT Parameters
    host = "a3o5xp6f0hhlk6.iot.us-east-1.amazonaws.com" 
    rootCAPath = "root-CA.crt"
    privateKeyPath = "RaspberryPi.private.key"
    certificatePath = "RaspberryPi.cert.pem"

    # MQTT Parameters
    host = "a3o5xp6f0hhlk6.iot.us-east-1.amazonaws.com" 
    rootCAPath = "root-CA.crt"
    privateKeyPath = "RaspberryPi.private.key"
    certificatePath = "RaspberryPi.cert.pem"
    
    MQTTClient.configureEndpoint(host, 8883)
    MQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

    ## AWSIoTMQTTClient connection configuration
    MQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
    MQTTClient.configureDrainingFrequency(100)  # Draining: 100 Hz
    MQTTClient.configureConnectDisconnectTimeout(5)  # 5 sec
    MQTTClient.configureMQTTOperationTimeout(3)  # 3 sec

    # Connect to AWS IoT
    MQTTClient.connect()

    return True

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    intent_value = intent_request["intent"]["slots"]["power_state"]["value"]

    if intent_name == "TV":
        if intent_value == "on":
            card_title = "TV Remote on"
            speech_output = "Turning on your television"
            should_end_session = True
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/tvRemote", "Turn on", 1)
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_value == "off":
            card_title = "TV Remote off"
            speech_output = "Turning off your television"
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/tvRemote", "Turn off", 1)
            # TODO: make sure the update was registered by Raspberry Pi
            should_end_session = True
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        else:
            raise ValueError("Invalid power state")
    else:
        raise ValueError("Invalid intent")

def get_welcome_response():
    session_attributes = {}
    card_title = "TV Remote"
    speech_output = "Welcome to the Alexa TV remote skill. " \
                    "You can ask me to turn on or off your tv."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, None, should_end_session))

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        "outputSpeech": {
            "type": "PlainText",
            "text": output
        },
        "card": {
            "type": "Simple",
            "title": title,
            "content": output
        },
        "reprompt": {
            "outputSpeech": {
                "type": "PlainText",
                "text": reprompt_text
            }
        },
        "shouldEndSession": should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        "version": "1.0",
        "sessionAttributes": session_attributes,
        "response": speechlet_response
    }

