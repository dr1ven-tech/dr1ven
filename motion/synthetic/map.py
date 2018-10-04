import json
import typing

from utils.log import Log

from state.section import Section


class SyntheticMap:
    def __init__(
            self,
            sections: typing.List[Section] = [],
    ) -> None:
        self._sections = sections

    def truncate(
            self,
            start: int,
            end: int,
    ) -> typing.List[Section]:
        return [s.truncate(start, end) for s in self._sections]

    def __iter__(
            self,
    ):
        yield 'sections', [dict(l) for l in self._sections]

    @staticmethod
    def from_dict(
            spec,
    ):
        return SyntheticMap(
            [Section.from_dict(s) for s in spec['sections']],
        )

    @staticmethod
    def from_file(
            path: str,
    ):
        Log.out("Loading map", {
            'path': path,
        })
        with open(path) as f:
            return SyntheticMap.from_dict(json.load(f))
