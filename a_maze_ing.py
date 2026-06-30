#!/usr/bin/env python3

import sys
import random


class ConfigErorr(Exception):
    def __init__(self, message: str = "Config Error") -> None:
        super().__init__(message)


class MazeGenerator():
    def __init__(self):
        self._birdview_16: dict[tuple, int] = {}
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
                self._cell[y * self._width + x] = [(x, y)]

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
                dx: int = coordinate1[0] - coordinate2[0]
                dy: int = coordinate1[1] - coordinate2[1]
                if dy == 0 and dx in (1, -1):
                    return coordinate1, coordinate2, 0
                if dx == 0 and dy in (1, -1):
                    return coordinate1, coordinate2, 1
        return None

    def _open_wall(self, cell: tuple, bit: int) -> None:
        if self._birdview_16[cell] & bit:
            self._birdview_16[cell] = self._birdview_16[cell] - bit

    def horz_break(self, cells: tuple[tuple, tuple, int]) -> None:
        cell1: tuple = cells[0]
        cell2: tuple = cells[1]
        if cell1[0] < cell2[0]:
            self._open_wall(cell1, 2)
            self._open_wall(cell2, 8)
        else:
            self._open_wall(cell1, 8)
            self._open_wall(cell2, 2)

    def vert_break(self, cells: tuple[tuple, tuple, int]) -> None:
        cell1: tuple = cells[0]
        cell2: tuple = cells[1]
        if cell1[1] < cell2[1]:
            self._open_wall(cell1, 4)
            self._open_wall(cell2, 1)
        else:
            self._open_wall(cell1, 1)
            self._open_wall(cell2, 4)

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
            if key1 == key2:
                continue

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
