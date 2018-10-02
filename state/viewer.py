import socketio
import eventlet
import eventlet.wsgi

from flask import Flask

from eventlet.green import threading

from state.constants import HIGHWAY_LANE_DEPTH
from state.highway import Highway
from state.lane import Lane, Section
from state.lane import RoadType
from state.entity import Entity, EntityOccupation
from state.entity import EntityType, EntityOrientation

_sio = socketio.Server(logging=False, engineio_logger=False)
_app = Flask(__name__)
_highway = None


@_sio.on('connect')
def connect(
        sid,
        environ,
):
    print("Received connect: sid={}".format(sid))
    _sio.emit('highway', dict(_highway))


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

    tD = RoadType.DRIVABLE
    tI = RoadType.INVALID
    tE = RoadType.EMERGENCY
    tP = RoadType.PARKING

    _highway = Highway(
        [
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [tD, tD, tD, tD, tD, tD, tD],
                ),
            ]),
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [tD, tD, tD, tD, tD, tD, tD],
                ),
            ]),
            Lane([
                Section(
                    0, HIGHWAY_LANE_DEPTH-1,
                    [tD, tD, tD, tD, tD, tD, tD],
                ),
            ]),
            Lane([
                Section(
                    0, 500,
                    [tE, tE, tE, tE, tE, tE, tI],
                ),
                Section(
                    500, 550,
                    [tE, tE, tE, tE, tE, tE, tP],
                ),
                Section(
                    550, HIGHWAY_LANE_DEPTH-1,
                    [tE, tE, tE, tE, tE, tE, tI],
                ),
            ]),
            Lane([
                Section(
                    0, 500,
                    [tI, tI, tI, tI, tI, tI, tI],
                ),
                Section(
                    500, 503,
                    [tP, tP, tP, tI, tI, tI, tI],
                ),
                Section(
                    503, 547,
                    [tP, tP, tP, tP, tP, tP, tP],
                ),
                Section(
                    547, 550,
                    [tP, tP, tP, tI, tI, tI, tI],
                ),
                Section(
                    550, HIGHWAY_LANE_DEPTH-1,
                    [tI, tI, tI, tI, tI, tI, tI],
                ),
            ]),
        ],
        Entity(
            EntityType.CAR,
            "4",
            EntityOccupation(
                EntityOrientation.FORWARD,
                2, [2, 600, 0], 4, 3,
            ),
            [0.0, 45.0, 0.0],
        ),
        [
            Entity(
                EntityType.CAR,
                "0",
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    0, [2, 850, 0], 4, 3,
                ),
                [-1.0, 60.0, 0.0],
            ),
            Entity(
                EntityType.TRUCK,
                "1",
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    2, [1, 950, 0], 6, 5,
                ),
                [-1.0, 40.0, 0.0],
            ),
            Entity(
                EntityType.TRAFFIC_CONE,
                "2",
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    3, [5, 650, 0], 1, 1,
                ),
                [0.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.TRAFFIC_CONE,
                "3",
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    3, [5, 654, 0], 1, 1,
                ),
                [0.0, 0.0, 0.0],
            ),
            Entity(
                EntityType.CAR,
                "5",
                EntityOccupation(
                    EntityOrientation.FORWARD,
                    2, [2, 610, 0], 4, 3,
                ),
                [0.0, 45.0, 0.0],
            ),
            Entity(
                EntityType.UNKNOWN,
                "6",
                EntityOccupation(
                    EntityOrientation.LATERAL,
                    1, [6, 597, 0], 6, 3,
                ),
                [0.0, 42.0, 0.0],
            ),
        ],
    )

    t = threading.Thread(target=run_server)
    t.start()
    t.join()
