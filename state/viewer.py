import sys
import socketio
import os
import eventlet
import eventlet.wsgi

import numpy as np

from flask import Flask
from flask import jsonify
from flask import abort
from flask import send_file

from eventlet.green import threading

from state.constants import HIGHWAY_LANE_DEPTH
from state.constants import HIGHWAY_LANE_WIDTH
from state.highway import Highway
from state.lane import Lane, Section
from state.lane import RoadType
from state.entity import Entity, EntityOccupation
from state.entity import EntityType, EntityOrientation

_sio = socketio.Server(logging=False, engineio_logger=False)
_app = Flask(__name__)
_highway = None

@_sio.on('connect')
def connect(sid, environ):
    print("Received connect: sid={}".format(sid))
    _sio.emit('highway', dict(_highway))

    print("{}".format(dict(_highway)['lanes']))

def run_server():
    global _app
    global _sio

    print("Starting shared server: port=9090")
    address = ('0.0.0.0', 9090)
    _app = socketio.Middleware(_sio, _app)
    try:
        eventlet.wsgi.server(eventlet.listen(address), _app)
    except KeyboardInterrupt:
        print("Stopping shared server")

def main():
    global _highway

    D = RoadType.DRIVABLE
    I = RoadType.INVALID
    E = RoadType.EMERGENCY
    P = RoadType.PARKING

    _highway = Highway(
        [
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [D, D, D, D, D, D, D],
                ),
            ]),
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [D, D, D, D, D, D, D],
                ),
            ]),
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [D, D, D, D, D, D, D],
                ),
            ]),
            Lane([
                Section(
                    0, 500,
                    [I, E, E, E, E, E, E],
                ),
                Section(
                    500, 550,
                    [P, E, E, E, E, E, E],
                ),
                Section(
                    550, HIGHWAY_LANE_DEPTH-1,
                    [I, E, E, E, E, E, E],
                ),
            ]),
            Lane([
                Section(
                    0, 500,
                    [I, I, I, I, I, I, I],
                ),
                Section(
                    500, 503,
                    [I, I, I, I, P, P, P],
                ),
                Section(
                    503, 547,
                    [P, P, P, P, P, P, P],
                ),
                Section(
                    547, 550,
                    [I, I, I, I, P, P, P],
                ),
                Section(
                    550, HIGHWAY_LANE_DEPTH-1,
                    [I, I, I, I, I, I, I],
                ),
            ]),
        ],
        [
            Entity(
                EntityType.CAR,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    0, [850, 2, 0], 4, 3,
                ),
                [60.0, -1.0, 0.0],
            ),
            Entity(
                EntityType.TRUCK,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    2, [950, 1, 0], 6, 5,
                ),
                [40.0, -1.0, 0.0],
            ),
            Entity(
                EntityType.TRAFFIC_CONE,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    3, [450, 6, 0], 1, 1,
                ),
                [0.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.TRAFFIC_CONE,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    3, [454, 6, 0], 1, 1,
                ),
                [0.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.EGO,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    2, [400, 2, 0], 4, 3,
                ),
                [45.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.CAR,
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    2, [410, 0, 0], 4, 3,
                ),
                [45.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.UNKNOWN,
                EntityOccupation(
                    EntityOrientation.LATERAL,
                    1, [397, 1, 0], 6, 3,
                ),
                [42.0, 0.0, 0.0],
            ),
        ],
    )

    t = threading.Thread(target = run_server)
    t.start()
    t.join()
