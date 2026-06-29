#!/usr/bin/env python3

import sys


class ConfigErorr(Exception):
    def __init__(self, message: str = "Config Error") -> None:
        super().__init__(message)


class MazeGenerator():
    def __init__(self):
        self._birdview_16: list[list[int]] = []
        self._birdview_2: list[list[int]] = []
        self._cell: dict[tuple[int, int], list[tuple]]

    class MazeData():
        def __init__(self):
            self._width: int
            self._height: int
            self._entry: tuple[int, int]
            self._exit: tuple[int, int]
            self._outputfile: str
            self._is_perfect: bool

        def set_config(self) -> None:
            with open(sys.argv[1]) as fd:
                raw_configs: list[str] = fd.readlines()
            if len(raw_configs) != 6:
                raise ConfigErorr
            config_value: list[str] = []
            for cnf in raw_configs:
                config_value.append(cnf.rstrip("\n").split("=")[1])
            if len(config_value) != 6:
                raise ConfigErorr
            self._width = int(config_value[0])
            if self._width < 2:
                raise ConfigErorr
            self._height = int(config_value[1])
            if self._height < 2:
                raise ConfigErorr
            entry: list[str] = (config_value[2]).split(",")
            self._entry = int(entry[0]), int(entry[1])
            if (
                    self._entry[0] < 0 or self._width < self._entry[0]
                    or self._entry[1] < 0 or self._height < self._entry[1]
                    ):
                raise ConfigErorr
            exit: list[str] = (config_value[3]).split(",")
            self._exit = int(exit[0]), int(exit[1])
            if (
                    self._exit[0] < 0 or self._width < self._exit[0]
                    or self._exit[1] < 0 or self._height < self._exit[1]
                    ):
                raise ConfigErorr
            self._outputfile = config_value[4]
            self._is_perfect = bool(config_value[5].capitalize())

    def describe_42(self) -> None:
        if self._width < 7 or self._height < 5:
            return

    def set_view_default(self) -> None:
        for y in range(self._height):
            for x in range(self._width):
                self._birdview_16[y][x] = 15
        for y in range(self._height):
            for x in range(self._width):
                if y % 2 == 0 or x % 2 == 0:
                    self._birdview_2[y][x] = 0
                else:
                    self._birdview_2[y][x] = 1

    def 
    def horz_break(self) -> None:

    def vert_break(self) -> None:
