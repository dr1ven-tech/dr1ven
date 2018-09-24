from symbolic.highway import Highway

class Command:
    def __init__(
            self,
            value,
            delta_time: float,
    ):
        self._value = value
        self._delta_time = delta_time

class Action:
    def __init__(
            self,
            forward: Command,
            lateral: Command,
    ):
        self._forward = self.forward
        self._lateral = self.lateral


class Agent:
    def __init__(
            self,
    ):
        pass

    def type(
            self,
    ) -> str:
        raise Exception("Not implemented")

    def action(
            self,
            time: float,
            state: Highway,
    ) -> Action:
        raise Exception("Not implemented")
