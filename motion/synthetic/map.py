import json
import typing

from utils.log import Log

from state.section import Section


class SyntheticMap:
    def __init__(
            self,
            sections: typing.List[Section] = [],
    ) -> None:
        assert len(sections) > 0
        slice_width = len(sections[0].slice())

        for s in sections:
            assert s.start() >= 0
            assert s.start() < s.end()
            assert len(s.slice()) == slice_width

        self._sections = sections

    def width(
            self,
    ) -> int:
        return len(self._sections[0].slice())

    def truncate(
            self,
            start: int,
            end: int,
    ) -> typing.List[Section]:
        sections = [s.truncate(start, end) for s in self._sections]
        sections = [s for s in sections if s is not None]

        return sections

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
