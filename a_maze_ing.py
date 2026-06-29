#!/usr/bin/env python3

import sys


class MazeGenerator():
    def __init__(self):
        self._birdview_16: list[int][int]
        self._birdview_2: list[int][int]
        self._cell: dict[tuple[int, int], list[tuple]]
    
    class MazeData():
        def __init__(self):
            self._width: int
            self._height: int
            self._entry: tuple[int, int]
            self._outputfile: str
            self._is_perfect: bool

        def read_config(self) -> None:
            try:
                with open(sys.argv[1]) as fd:
                    raw_configs: list[str] = fd.readlines()
            except Exception as e:
                print(e)
            configs: list[str] = []
            for cnf in raw_configs:
                configs.append(cnf.rstrip("\n"))
            return configs


