""" based on fauxmo_minimal.py by Fabricate.IO
    git repo: https://github.com/toddmedema/echo/

    Author: Roshun Alur
"""

import fauxmo
import logging
import time
import subprocess

from debounce_handler import debounce_handler

logging.basicConfig(level=logging.CRITICAL) # Only print CRITICAL messages

# NOTE: Make sure you update this with your remote's name!!
remote_name = "vizio"

class device_handler(debounce_handler):
    """Handles requests from Alexa"""
    # For this project, we're using the trigger "the tv" and listening on port 52000
    TRIGGERS = {"the tv": 52000}

    # Function to perform a series of actions when a trigger is received from Alexa
    def act(self, client_address, state):
        logging.debug("State", state, "from client @", client_address)
        # Open subprocess to send IR command using irsend
        subprocess.Popen("irsend SEND_ONCE %s KEY_POWER" % remote_name, shell=True) 
        return True

if __name__ == "__main__":
    # Startup the fauxmo server
    fauxmo.DEBUG = True
    p = fauxmo.poller()
    u = fauxmo.upnp_broadcast_responder()
    u.init_socket()
    p.add(u)

    # Register the device callback as a fauxmo handler
    d = device_handler()
    for trig, port in d.TRIGGERS.items():
        fauxmo.fauxmo(trig, u, p, None, port, d)

    # Loop and poll for incoming Echo requests
    logging.debug("Entering fauxmo polling loop")
    while True:
        try:
            # Allow time for a ctrl-c to stop the process
            p.poll(100)
            time.sleep(0.1)
        except Exception, e:
            logging.critical("Critical exception: " + str(e))
            break
