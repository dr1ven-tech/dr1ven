import argparse
import cv2
import io
import json
import eventlet
import eventlet.wsgi
import os

from flask import Flask
from flask import render_template, send_file, abort

from eventlet.green import threading

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario

_app = Flask(__name__)
_config = None


@_app.before_first_request
def setup():
    global _config

    if _config is None:
        Log.out(
            "Defaulting config", {
                'path': "configs/dev.json",
            })

        _config = Config.from_file("configs/dev.json")


#
# planning.synthetic
#


@_app.route('/scenarios/planning.synthetic/<scenario>')
def view_scenarios_planning_synthetic(scenario):

    dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    dump_path = os.path.join(dump_dir, "dump.json")

    with open(dump_path) as f:
        dump = json.load(f)

        return render_template(
            'scenarios_planning_synthetic.html',
            dump=dump,
        )


#
# perception.bbox
#


@_app.route('/scenarios/perception.bbox/<scenario>')
def view_scenarios_perception_bbox(scenario):

    dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    dump_path = os.path.join(dump_dir, "dump.json")

    with open(dump_path) as f:
        dump = json.load(f)

        return render_template(
            'scenarios_perception_bbox.html',
            dump=dump,
        )


@_app.route('/scenarios/perception.bbox/<scenario>/image')
def view_scenarios_perception_bbox_image(scenario):

    dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    image_path = os.path.join(dump_dir, "image.png")

    image = cv2.imread(image_path)
    _, encoded = cv2.imencode('.png', image)

    return send_file(
        io.BytesIO(encoded.tobytes()),
        attachment_filename='image.png',
        mimetype='image/png',
    )


#
# perception.stereo
#


@_app.route('/scenarios/perception.stereo/<scenario>')
def view_scenarios_perception_stereo(scenario):

    # dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    # dump_path = os.path.join(dump_dir, "dump.json")

    # with open(dump_path) as f:
    #     dump = json.load(f)

    return render_template(
        'scenarios_perception_stereo.html',
        dump="",
    )


@_app.route('/scenarios/perception.stereo/<scenario>/images/<side>')
def view_scenarios_perception_stereo_images(scenario, side):

    if side not in ['left', 'right']:
        abort(400)

    dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    image_path = os.path.join(dump_dir, side + ".png")

    image = cv2.imread(image_path)
    _, encoded = cv2.imencode('.png', image)

    return send_file(
        io.BytesIO(encoded.tobytes()),
        attachment_filename=side + ".png",
        mimetype='image/png',
    )


def run_server():
    global _app

    Log.out(
        "Starting viewer server", {
            'port': 5000,
        })
    address = ('0.0.0.0', 5000)
    try:
        eventlet.wsgi.server(eventlet.listen(address), _app)
    except KeyboardInterrupt:
        Log.out(
            "Stopping viewer server", {})


def main():
    global _config

    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'config_path',
        type=str, help="path to the config file",
    )

    args = parser.parse_args()

    _config = Config.from_file(args.config_path)

    t = threading.Thread(target=run_server)
    t.start()
    t.join()
