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
from symbolic.entity import Entity, EntityType, EntityOccupation, EntityOrientation

_sio = socketio.Server(logging=False, engineio_logger=False)
_app = Flask(__name__)
_highway = None

@_sio.on('connect')
def connect(sid, environ):
    print("Received connect: sid={}".format(sid))

    map_specification = []
    for lane in _highway._map._specification:
        l = []
        for s in lane:
            l.append([
                s[0], s[1], [t.value for t in s[2]]
            ])
        map_specification.append(l)

    entities = []
    for e in _highway._entities:
        entities.append({
            'type': e.type().value,
            'occupation': [
                e.occupation()._orientation.value,
                e.occupation()._lane,
                e.occupation()._position,
                e.occupation()._width,
                e.occupation()._height,
            ]
        })

    _sio.emit('highway', {
        'map': map_specification,
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
                [RoadType.INVALID] + \
                [RoadType.EMERGENCY] * (HIGHWAY_LANE_WIDTH-1),
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH,
            ],
        ],
        [
            [
                0, HIGHWAY_LANE_DEPTH,
                [RoadType.INVALID] * HIGHWAY_LANE_WIDTH,
            ],
        ],
    ])

    _highway.set_map(m)

    _highway.add_entity(
        Entity(
            EntityType.CAR,
            EntityOccupation(
                EntityOrientation.FORWARD,
                0, [850, 2, 0], 4, 3,
            ),
            np.array([60.0, -1.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRUCK,
            EntityOccupation(
                EntityOrientation.FORWARD,
                2, [950, 1, 0], 6, 5,
            ),
            np.array([40.0, -1.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRAFFIC_CONE,
            EntityOccupation(
                EntityOrientation.FORWARD,
                3, [450, 6, 0], 1, 1,
            ),
            np.array([0.0, 0.0, 0.0]),
        ),
    )
    _highway.add_entity(
        Entity(
            EntityType.TRAFFIC_CONE,
            EntityOccupation(
                EntityOrientation.FORWARD,
                3, [454, 6, 0], 1, 1,
            ),
            np.array([0.0, 0.0, 0.0]),
        ),
    )

    _highway.add_entity(
        Entity(
            EntityType.EGO,
            EntityOccupation(
                EntityOrientation.FORWARD,
                2, [400, 2, 0], 4, 3,
            ),
            np.array([45.0, 0.0, 0.0]),
        ),
    )

    _highway.add_entity(
        Entity(
            EntityType.CAR,
            EntityOccupation(
                EntityOrientation.FORWARD,
                2, [410, 0, 0], 4, 3,
            ),
            np.array([45.0, 0.0, 0.0]),
        ),
    )

    _highway.add_entity(
        Entity(
            EntityType.UNKNOWN,
            EntityOccupation(
                EntityOrientation.LATERAL,
                1, [397, 1, 0], 6, 3,
            ),
            np.array([42.0, 0.0, 0.0]),
        ),
    )

    t = threading.Thread(target = run_server)
    t.start()
    t.join()
