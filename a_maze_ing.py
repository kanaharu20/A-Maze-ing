#!/usr/bin/env python3

import sys
import random


class ConfigErorr(Exception):
    def __init__(self, message: str = "Config Error") -> None:
        super().__init__(message)


class MazeGenerator():
    def __init__(self):
        self._birdview_16: dict[tuple, int] = {}
        self._birdview_2: dict[tuple, int] = {}
        self._cell: dict[int, list[tuple]] = {}
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
                self._entry[0] < 0 or self._width <= self._entry[0]
                or self._entry[1] < 0 or self._height <= self._entry[1]
        ):
            raise ConfigErorr
        exit: list[str] = (config_value[3]).split(",")
        self._exit = int(exit[0]), int(exit[1])
        if (
                self._exit[0] < 0 or self._width <= self._exit[0]
                or self._exit[1] < 0 or self._height <= self._exit[1]
        ):
            raise ConfigErorr
        self._outputfile = config_value[4]
        self._is_perfect = config_value[5].strip() == "True"

    # def describe_42(self) -> None:
    #     if self._width < 7 or self._height < 5:
    #         return

    def set_view_default(self) -> None:
        for y in range(self._height):
            for x in range(self._width):
                self._birdview_16[x, y] = 15
        for y in range(self._height):
            for x in range(self._width):
                if y % 2 == 0 or x % 2 == 0:
                    self._birdview_2[x, y] = 0
                else:
                    self._birdview_2[x, y] = 1
                    # 1の時に壁を意味している

    def fetch_random_cell_num(self) -> int:
        return random.choice(list(self._cell.keys()))

    def varidate(self, cell1_num: int, cell2_num: int) -> tuple[
            tuple,
            tuple,
            int] | None:
        cell1_coordinates: list[tuple] = self._cell[cell1_num]
        cell2_coordinates: list[tuple] = self._cell[cell2_num]
        for coordinate1 in cell1_coordinates:
            for coordinate2 in cell2_coordinates:
                if coordinate1[0] - coordinate2[0] == 1:
                    if not all(
                            (coordinate1[0] - coordinate2[0] in (1, -1),
                             coordinate1[1] - coordinate2[1] in (1, -1))):
                        if self._birdview_2[coordinate1[0]*2 - 1] == 1:
                            return coordinate1, coordinate2, 0
                if coordinate1[0] - coordinate2[0] == -1:
                    if not all(
                            (coordinate1[0] - coordinate2[0] in (1, -1),
                             coordinate1[1] - coordinate2[1] in (1, -1))):
                        if self._birdview_2[coordinate2[0]*2 - 1] == 1:
                            return coordinate1, coordinate2, 0
                if coordinate1[1] - coordinate2[1] == 1:
                    if not all(
                            (coordinate1[0] - coordinate2[0] in (1, -1),
                             coordinate1[1] - coordinate2[1] in (1, -1))):
                        if self._birdview_2[coordinate1[1]*2 - 1] == 1:
                            return coordinate1, coordinate2, 0
                if coordinate1[1] - coordinate2[1] == -1:
                    if not all(
                            (coordinate1[0] - coordinate2[0] in (1, -1),
                             coordinate1[1] - coordinate2[1] in (1, -1))):
                        if self._birdview_2[coordinate2[0]*2 - 1] == 1:
                            return coordinate1, coordinate2, 0

    def horz_break(self, cells: tuple[tuple, tuple, int]) -> None:
        x1: int = cells[0][0]
        x2: int = cells[1][0]
        if x1 < x2:
            self._birdview_16[x1] = self._birdview_16[x1] - 2
            self._birdview_16[x2] = self._birdview_16[x2] - 8
            self._birdview_2[x1*2+1] = 0
        else:
            self._birdview_16[x1] = self._birdview_16[x1] - 8
            self._birdview_16[x2] = self._birdview_16[x2] - 2
            self._birdview_2[x1*2-1] = 0

    def vert_break(self, cells: tuple[tuple, tuple, int]) -> None:
        y1: int = cells[0][1]
        y2: int = cells[1][1]
        if y1 < y2:
            self._birdview_16[y1] = self._birdview_16[y1] - 4
            self._birdview_16[y2] = self._birdview_16[y2] - 1
            self._birdview_2[y1*2+1] = 0
        else:
            self._birdview_16[y1] = self._birdview_16[y1] - 1
            self._birdview_16[y2] = self._birdview_16[y2] - 4
            self._birdview_2[y1*2-1] = 0

    def manage_cell_num(self, key1: int, key2: int) -> None:
        if key1 < key2:
            self._cell[key1].extend(self._cell[key2])
            del self._cell[key2]
        else:
            self._cell[key2].extend(self._cell[key1])
            del self._cell[key1]

    def is_a_maze(self) -> bool:
        if len(self._cell) == 1:
            return True
        else:
            return False

    def save_a_maze(self) -> None:
        output: str = ""
        for y in range(self._height):
            for x in range(self._width):
                output = output+format(self._birdview_16[(x, y)], "x")
            output = output+"\n"

        try:
            with open(self._outputfile, "w") as fd:
                fd.write(output)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    def main() -> None:
        tst_gen: MazeGenerator = MazeGenerator()
        tst_gen.set_config()
        tst_gen.set_view_default()
        while True:
            key1: int = tst_gen.fetch_random_cell_num()
            key2: int = tst_gen.fetch_random_cell_num()

            result: tuple[
                tuple,
                tuple,
                int] | None = tst_gen.varidate(key1, key2)

            if result is not None:
                if result[2] == 0:
                    tst_gen.horz_break(result)
                else:
                    tst_gen.vert_break(result)
                tst_gen.manage_cell_num(key1, key2)
            if tst_gen.is_a_maze():
                break
        tst_gen.save_a_maze()

    main()
