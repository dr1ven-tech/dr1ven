from state.highway import Highway

class Command:
    def __init__(
            self,
            value,
            delta: float,
    ) -> None:
        self._value = value
        self._delta = delta

    def value(
            self,
    ):
        return self._value

    def delta(
            self,
    ) -> float:
        return self._delta

class Action:
    def __init__(
            self,
            forward: Command,
            lateral: Command,
    ) -> None:
        self._forward = forward
        self._lateral = lateral

    def forward(
            self,
    ) -> Command:
        return self._forward

    def lateral(
            self,
    ) -> Command:
        return self._lateral

class Agent:
    def __init__(
            self,
    ) -> None:
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
