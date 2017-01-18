import json
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import random

myAWSIoTMQTTClient = AWSIoTMQTTClient("basicPubSub")

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

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
    MQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    MQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
    MQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
    MQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

    return True

def on_session_started(session_started_request, session):
    print "Starting new session."

def on_launch(launch_request, session):
    return get_welcome_response()

def on_intent(intent_request, session):
    intent = intent_request["intent"]
    intent_name = intent_request["intent"]["name"]
    if intent_name != "clear":
        try:
            intent_type = "power_state"
            intent_value = intent_request["intent"]["slots"]["power_state"]["value"]
        except KeyError:
            try:
                intent_type = "video_service"
                intent_value = intent_request["intent"]["slots"]["video_service"]["value"]
            except KeyError:
                try:
                    intent_type = "button"
                    intent_value = intent_request["intent"]["slots"]["button"]["value"]
                except KeyError:
                    try:
                        intent_type = "direction"
                        intent_value = intent_request["intent"]["slots"]["direction"]["value"]
                    except KeyError:
                        try:
                            intent_type = "search"
                            intent_value = intent_request["intent"]["slots"]["search"]["value"]
                        except KeyError:
                            intent_type = "volume_direction"
                            intent_value = intent_request["intent"]["slots"]["volume_direction"]["value"]
                            try:
                                volume_amount = intent_request["intent"]["slots"]["volume_amount"]["value"]
                            except KeyError:
                                volume_amount = 1

    if intent_name == "AppleTV":
        if intent_type == "button":
            card_title = "Apple TV Remote press " + intent_value
            speech_output = "Pressing " + intent_value + " on your Apple TV"
            should_end_session = True
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/appleTvRemote", intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/appleTRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/appleTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_type == "direction":            
            card_title = "Apple TV Remote move " + intent_value
            speech_output = "Moving " + intent_value + " on your Apple TV"
            should_end_session = True
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/appleTvRemote", intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/appleTvRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/appleTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        else:
            raise ValueError("Invalid power state")
    elif intent_name == "Vizio":
        if intent_type == "button":
            card_title = "Vizio TV Remote press " + intent_value
            speech_output = "Pressing " + intent_value + " on your Vizio TV"
            should_end_session = True
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", intent_type + " " + intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_type == "power_state":
            card_title = "Vizio TV Remote turn " + intent_value
            speech_output = "Turning " + intent_value + " your Vizio TV"
            should_end_session = True
            # Publish to MQTT here
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", intent_type + " " + intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_type == "volume_direction":
            card_title = "Vizio TV Remote turning volume " + intent_value + " by " + str(volume_amount) 
            speech_output = "Turning the volume " + intent_value + " by " + str(volume_amount) + " on your Vizio TV"
            should_end_session = True
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", "volume" + " " + intent_value + " " + str(volume_amount), 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_type == "search":
            card_title = "Vizio TV Remote search for " + intent_value
            speech_output = "Searching for " + intent_value + " on your Vizio TV"
            should_end_session = True
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", intent_type + " " + intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
        elif intent_type == "video_service":
            card_title = "Vizio TV Remote opening video service " + intent_value
            speech_output = "Opening the " + intent_value + " app on your Vizio TV"
            should_end_session = True
            myAWSIoTMQTTClient.connect()
            myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", intent_type + " " + intent_value, 1)
            myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, customCallback)
            myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioTvRemote")
            myAWSIoTMQTTClient.disconnect()
            # TODO: make sure the update was registered by Raspberry Pi
            return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    elif intent_name == "clear":
        card_title = "Vizio TV remote: clearing the search bar"
        speech_output = "Clearing the search bar on your Vizio TV"
        should_end_session = True
        # Publish to MQTT here
        myAWSIoTMQTTClient.connect()
        myAWSIoTMQTTClient.publish("$aws/things/RaspberryPi/vizioTvRemote", intent_name, 1)
        myAWSIoTMQTTClient.subscribe("$aws/things/RaspberryPi/vizioTRemote", 1, customCallback)
        myAWSIoTMQTTClient.unsubscribe("$aws/things/RaspberryPi/vizioRemote")
        myAWSIoTMQTTClient.disconnect()
        # TODO: make sure the update was registered by Raspberry Pi
        return build_response({}, build_speechlet_response(card_title, speech_output, None, should_end_session))
    else:
        raise ValueError("Invalid intent: " + intent_name)

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
