from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import logging
import time
import subprocess
from time import gmtime, strftime

import argparse


def vizio_search(message):
    # Navigate to the Netflix search screen
    # TODO: handle searching after a previous search versus searching from scratch, maybe use a different keyword?
    subprocess.Popen("irsend SEND_ONCE vizio KEY_NETFLIX", shell=True)
    time.sleep(3)
    subprocess.Popen("irsend SEND_ONCE vizio KEY_OK", shell=True)
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
    return True


# Custom MQTT message callback
def callback(client, userdata, message):
    repetition = 1
    if message.payload.split()[0] == "search":
        vizio_search(message.payload.replace("search ",""))
    elif message.payload.split()[0] == "clear":
        vizio_clear()
    elif message.payload.split()[0] == "video_service":
        vizio_open_video_service(message.payload.upper().split()[1])
    else:
        button = ''
        if message.payload.upper().split()[1] == "OKAY":
            button = "KEY_OK"
        elif (message.payload.upper().split()[1] == "ON" or message.payload.upper().split()[1] == "OFF") \
                and message.payload.split()[0] == "power_state":
            button = "KEY_POWER"
        elif message.payload.split()[0] == "volume":
            if message.payload.upper().split()[1] == "UP":
                button = "KEY_VOLUMEUP"
                repetition = int(message.payload.split()[2])
                # print "Turning volume up by %s" % repetition
            elif message.payload.upper().split()[1] == "DOWN":
                button = "KEY_VOLUMEDOWN"
                repetition = int(message.payload.split()[2])
                # print "Turning volume down by %s" % repetition
            # TODO: build in some error handling here for incorrect volume settings
        else:
            button = "KEY_" + message.payload.upper().split()[1]
        for i in range(repetition):
            subprocess.Popen("irsend SEND_ONCE vizio " + button, shell=True)
            time.sleep(0.3)
    
    with open("/home/pi/alexa_remote_commands_vizio.log", "a") as command_logger:
        command_logger.write(strftime("%Y-%m-%d %H:%M:%S", gmtime()) +
                             "\t" + message.topic + "\t" + message.payload + "\n")


def parse_args():
    # Usage
    usage = """
    Use certificate based mutual authentication:
    python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -c <certFilePath> -k <privateKeyFilePath>

    Use MQTT over WebSocket:
    python basicPubSub.py -e <endpoint> -r <rootCAFilePath> -w

    Type "python basicPubSub.py -h" for available options.
    """
    parser = argparse.ArgumentParser(usage=usage)
    parser.add_argument('-e', '--endpoint', required=True, help='Your AWS IoT custom endpoint')
    parser.add_argument('-r', '--rootCA', required=True, help='Root CA file path')
    parser.add_argument('-c', '--cert', required=False, help='Certificate file path')
    parser.add_argument('-k', '--key', required=False, help='Private key file path')
    parser.add_argument('-w', '--websocket', default=False, help='Use MQTT over WebSocket')
    args = parser.parse_args()

    # Some logic
    if not args.websocket:
        if not args.cert:
            parser.error("Missing '-c' or '--cert'")
        if not args.key:
            parser.error("Missing '-k' or '--key'")

    return args


def configure_logging():
    # Configure logging
    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def main():
    args = parse_args()
    configure_logging()

    # Init AWSIoTMQTTClient
    if args.websocket:
        client = AWSIoTMQTTClient("basicSub", useWebsocket=True)
        client.configureEndpoint(args.endpoint, 443)
        client.configureCredentials(args.rootCA)
    else:
        client = AWSIoTMQTTClient("basicSub")
        client.configureEndpoint(args.endpoint, 8883)
        client.configureCredentials(args.rootCA, args.key, args.cert)

    # AWSIoTMQTTClient connection configuration
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec

    # Connect and subscribe to AWS IoT
    client.connect()
    client.subscribe("$aws/things/RaspberryPi/vizioTvRemote", 1, callback)
    time.sleep(2)

    # Wait in an infinite loop
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()