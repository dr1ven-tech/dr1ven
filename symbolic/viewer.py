import sys
import io
import os
import eventlet
import eventlet.wsgi

import numpy as np

from flask import Flask
from flask import jsonify
from flask import abort
from flask import send_file

from eventlet.green import threading

_app = Flask(__name__)

def run_server():
    global _app
    cwd = os.getcwd()
    print("CWD {}".format(cwd))
    print("Starting shared server: port=9090")
    address = ('0.0.0.0', 9090)
    try:
        eventlet.wsgi.server(eventlet.listen(address), _app)
    except KeyboardInterrupt:
        print("Stopping shared server")

def main():
    t = threading.Thread(target = run_server)
    t.start()
    t.join()
