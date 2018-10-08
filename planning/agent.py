from state.highway import Highway


class Command:
    """ `Command` reprensents a change of position over a period of time.

    It is used to represent a target position (in `state.Highway` space) at a
    target time. It is expressed in absolute coordinates in `state.Highway`.
    """
    def __init__(
            self,
            position: int,
            delta: float,
    ) -> None:
        self._position = position
        self._delta = delta

    def position(
            self,
    ) -> int:
        return self._position

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
