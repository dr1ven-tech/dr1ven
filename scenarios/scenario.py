import argparse
import datetime
import importlib
import json
import os

from utils.config import Config
from utils.log import Log


class ScenarioSpec:
    def __init__(
            self,
            module: str,
            type: str,
            data,
    ) -> None:
        self._module = module
        self._type = type
        self._data = data

    def module(
            self,
    ) -> str:
        return self._module

    def type(
            self,
    ) -> str:
        return self._type

    def data(
            self,
    ):
        return self._data

    def scenario(
            self,
            config: Config,
    ):
        m = importlib.import_module(self._module)
        klass = getattr(m, self._type)
        return klass(config, self)

    @staticmethod
    def from_dict(
            spec,
    ):
        return ScenarioSpec(
            spec['module'],
            spec['type'],
            spec['data'],
        )

    @staticmethod
    def from_file(
            path: str,
    ):
        with open(path) as f:
            return ScenarioSpec.from_dict(json.load(f))


class Scenario:
    """ `Scenario` represents a generic runnable functional test scenario.

    The generic behavior consists in:
    - The ability to run itself given the current config and a `ScenarioSpec`.
    - The ability to construt an URL to a viewer to introspect the scenario.

    Scenarios are expected to dump their state as they run for later viewing
    and introspection.
    """

    def __init__(
            self,
            config: Config,
            spec: ScenarioSpec,
    ) -> None:
        self._config = config
        self._spec = spec

        self._id = "{}-{}.{}".format(
            datetime.datetime.now().strftime("%Y%m%d_%H%M_%S.%f"),
            spec.module(),
            spec.type(),
        )

        self._dump_dir = os.path.join(
            os.path.expanduser(config.get('scenarios_dump_dir')),
            self._id,
        )

    def id(
            self,
    ) -> str:
        return self._id

    def dump_dir(
            self,
    ) -> str:
        return self._dump_dir

    def run(
            self,
    ) -> bool:
        """ `run` triggers the execution of the `Scenario`.
        """
        raise Exception("Not implemented")

    def view(
            self,
    ) -> str:
        """ `view` returns an URL to view the `Scenario`.
        """
        raise Exception("Not implemented")


def run():
    parser = argparse.ArgumentParser(description="")

    parser.add_argument(
        'config_path',
        type=str, help="path to the config file",
    )
    parser.add_argument(
        'spec_path',
        type=str, help="path to the spec file",
    )

    args = parser.parse_args()

    config = Config.from_file(args.config_path)
    spec = ScenarioSpec.from_file(args.spec_path)

    scenario = spec.scenario(config)

    Log.out(
        "Starting scenario", {
            'id': scenario.id(),
            'dump_dir': scenario.dump_dir(),
        })

    scenario.run()

    Log.out(
        "Finished scenario", {
            'id': scenario.id(),
        })
