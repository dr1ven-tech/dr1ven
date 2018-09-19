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

from symbolic.constants import HIGHWAY_LANE_DEPTH
from symbolic.constants import HIGHWAY_LANE_WIDTH
from symbolic.highway import Highway
from symbolic.map import Map, RoadType
from symbolic.entity import Entity, EntityType

_sio = socketio.Server(logging=False, engineio_logger=False)
_app = Flask(__name__)
_highway = None

@_sio.on('connect')
def connect(sid, environ):
    print("Received connect: sid={}".format(sid))
    entities = []
    for e in _highway._entities:
        entities.append({
            'occupation': e._occupation,
            'type': e.type().value,
        })

    _sio.emit('highway', {
        'map': _highway._map._component.tolist(),
        'entities': entities,
    })

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

    _highway = Highway()

    m = Map([
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.DRIVABLE] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.DRIVABLE] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.DRIVABLE] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.EMERGENCY] * (HIGHWAY_LANE_WIDTH-1) + \
                [RoadType.INVALID],
            ],
        ],
    ])

    _highway.set_map(m)

    _highway.add_entity(
        Entity(
            EntityType.CAR,
            Entity.forward_occupation(
                0, 850, 4, 3, 2,
            ),
            np.array([60.0, -1.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRUCK,
            Entity.forward_occupation(
                2, 950, 6, 5, 1,
            ),
            np.array([40.0, -1.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRAFFIC_CONE,
            Entity.forward_occupation(
                3, 450, 1, 1, 6,
            ),
            np.array([0.0, 0.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRAFFIC_CONE,
            Entity.forward_occupation(
                3, 454, 1, 1, 6,
            ),
            np.array([0.0, 0.0, 0.0]),
        ),
    )

    _highway.add_entity(
        Entity(
            EntityType.EGO,
            Entity.forward_occupation(
                2, 400, 4, 3, 1,
            ),
            np.array([45.0, 0.0, 0.0]),
        ),
    )

    t = threading.Thread(target = run_server)
    t.start()
    t.join()
