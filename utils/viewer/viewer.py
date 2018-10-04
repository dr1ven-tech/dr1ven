import argparse
import json
import eventlet
import eventlet.wsgi
import os

from flask import Flask
from flask import render_template

from eventlet.green import threading

from utils.config import Config
from utils.log import Log
from utils.scenario import Scenario

_app = Flask(__name__)
_config = None


@_app.route('/scenarios/planning/synthetic/<scenario>')
def view_scenarions_planning_synthetic(scenario):

    dump_dir = Scenario.dump_dir_for_id(_config, scenario)
    dump_path = os.path.join(dump_dir, "dump.json")

    with open(dump_path) as f:
        dump = json.load(f)

        return render_template(
            'scenarios_planning_synthetic.html',
            dump=dump,
        )


def run_server():
    global _app

    Log.out(
        "Starting viewer server", {
            'port': 9090,
        })
    address = ('0.0.0.0', 9090)
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
