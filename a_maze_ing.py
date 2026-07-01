#!/usr/bin/env python3

import sys
import random
from collections import deque


class ConfigErorr(Exception):
    """Exception raised when the maze configuration is invalid.

    Raised whenever the configuration file is missing required keys,
    contains malformed values, or describes a maze that cannot be
    generated (e.g. out-of-bounds entry/exit coordinates).
    """

    def __init__(self, message: str = "Configuration Error") -> None:
        """Initialize the exception with a descriptive message.

        Args:
            message: Human-readable description of the configuration
                error. Defaults to "Configuration Error".
        """
        super().__init__(message)


class MazeGenerator():
    """Generates, solves, and serializes a maze from a configuration file.

    The maze is represented internally as a bird's-eye view mapping each
    cell's coordinates to a 4-bit wall bitmask (1=North, 2=East, 4=South,
    8=West). Cells are grouped into disjoint sets keyed by an integer
    cell number; merging two sets by breaking the wall between them is
    how the maze is carved.
    """

    def __init__(self) -> None:
        """Initialize an empty maze generator with no configuration loaded."""
        self._birdview_16: dict[tuple, int] = {}
        self._cell: dict[int, list[tuple]] = {}
        self._width: int
        self._height: int
        self._entry: tuple[int, int]
        self._exit: tuple[int, int]
        self._outputfile: str
        self._is_perfect: bool
        self._ans: list[str] = []

    def set_config(self) -> None:
        """Load and validate the maze configuration from the CLI argument.

        Reads the file path given as the first command-line argument,
        parses it as six ``KEY=VALUE`` lines, and populates the width,
        height, entry, exit, output file, and perfect-maze attributes.

        Raises:
            ConfigErorr: If the file does not contain exactly six lines,
                contains unknown or duplicate keys, or if the width,
                height, entry, or exit values are invalid or out of
                bounds.
        """
        configs: dict[str, str] = {}
        with open(sys.argv[1]) as fd:
            raw_configs: list[str] = fd.readlines()
        if len(raw_configs) != 6:
            raise ConfigErorr
        for cnf in raw_configs:
            key_value: list[str] = cnf.rstrip("\n").split("=")
            configs[key_value[0]] = int(key_value[1])
        if len(configs.keys()) != 6:
            raise ConfigErorr
        for conf in configs.keys():
            if conf not in [
                "WIDTH", "HEGHT", "ENTRY",
                "EXIT", "PERFECT", "OUTPUT_FILE"
                    ]:
                raise ConfigErorr
        self._width = int(configs["WIDTH"])
        if self._width < 2:
            raise ConfigErorr
        self._height = int(configs["HEIGHT"])
        if self._height < 2:
            raise ConfigErorr
        entry: list[str] = (configs["ENTRY"]).split(",")
        self._entry = int(entry[0]), int(entry[1])
        if (
                self._entry[0] < 0 or self._width <= self._entry[0]
                or self._entry[1] < 0 or self._height <= self._entry[1]
        ):
            raise ConfigErorr
        exit: list[str] = (configs["EXIT"]).split(",")
        self._exit = int(exit[0]), int(exit[1])
        if (
                self._exit[0] < 0 or self._width <= self._exit[0]
                or self._exit[1] < 0 or self._height <= self._exit[1]
        ):
            raise ConfigErorr
        self._outputfile = configs["OUTPUT_FILE"]
        self._is_perfect = configs["PERFECT"] == "True"

    def set_view_default(self) -> None:
        """Initialize the bird's-eye view and per-cell grouping.

        Sets every cell's wall bitmask to fully closed (15) and creates
        one singleton group per cell in ``self._cell``. When the maze is
        large enough (width >= 7 or height >= 5), the cells forming the
        "42" pattern are excluded from ``self._cell`` so they remain
        permanently isolated (fully closed) in the final maze.
        """
        s: int = self._width/2
        t: int = self._height/2
        if self._width >= 7 or self._height >= 5:
            forty_two: list[tuple] = [
                (s - 3, t - 2), (s + 1, t - 2), (s + 2, t - 2),
                (s + 3, t - 2), (s - 3, t - 1), (s + 3, t - 1),
                (s - 3, t), (s - 2, t), (s - 1, t), (s + 1, t),
                (s + 2, t), (s + 3, t), (s - 1, t + 1), (s + 1, t + 1),
                (s - 1, t + 2), (s + 1, t + 2), (s + 2, t + 2), (s + 3, t + 2)
            ]
            for y in range(self._height):
                for x in range(self._width):
                    self._birdview_16[x, y] = 15
                    if not (x, y) in forty_two:
                        self._cell[y * self._width + x] = [(x, y)]
        else:
            for y in range(self._height):
                for x in range(self._width):
                    self._birdview_16[x, y] = 15
                    self._cell[y * self._width + x] = [(x, y)]

    def fetch_random_cell_num(self) -> int:
        """Pick a random cell group key from the current cell groups.

        Returns:
            A key of ``self._cell`` chosen uniformly at random.
        """
        return random.choice(list(self._cell.keys()))

    def varidate(self, cell1_num: int, cell2_num: int) -> tuple[
            tuple,
            tuple,
            int] | None:
        """Check whether two cell groups are adjacent and can be merged.

        Args:
            cell1_num: Key identifying the first cell group.
            cell2_num: Key identifying the second cell group.

        Returns:
            A tuple ``(coordinate1, coordinate2, orientation)`` for the
            first pair of adjacent coordinates found between the two
            groups, where ``orientation`` is 0 for a horizontal
            (east-west) adjacency and 1 for a vertical (north-south)
            adjacency. Returns ``None`` if no adjacent coordinates exist
            between the two groups.
        """
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
        """Clear a single wall bit for the given cell, if it is set.

        Args:
            cell: Coordinates of the cell whose wall should be opened.
            bit: Bitmask of the wall to clear (1=North, 2=East, 4=South,
                8=West).
        """
        if self._birdview_16[cell] & bit:
            self._birdview_16[cell] = self._birdview_16[cell] - bit

    def horz_break(self, cells: tuple[tuple, tuple, int]) -> None:
        """Open the shared wall between two horizontally adjacent cells.

        Args:
            cells: A ``(coordinate1, coordinate2, orientation)`` tuple as
                returned by :meth:`varidate`, where ``coordinate1`` and
                ``coordinate2`` are horizontally adjacent (differ only in
                x).
        """
        cell1: tuple = cells[0]
        cell2: tuple = cells[1]
        if cell1[0] < cell2[0]:
            self._open_wall(cell1, 2)
            self._open_wall(cell2, 8)
        else:
            self._open_wall(cell1, 8)
            self._open_wall(cell2, 2)

    def vert_break(self, cells: tuple[tuple, tuple, int]) -> None:
        """Open the shared wall between two vertically adjacent cells.

        Args:
            cells: A ``(coordinate1, coordinate2, orientation)`` tuple as
                returned by :meth:`varidate`, where ``coordinate1`` and
                ``coordinate2`` are vertically adjacent (differ only in
                y).
        """
        cell1: tuple = cells[0]
        cell2: tuple = cells[1]
        if cell1[1] < cell2[1]:
            self._open_wall(cell1, 4)
            self._open_wall(cell2, 1)
        else:
            self._open_wall(cell1, 1)
            self._open_wall(cell2, 4)

    def manage_cell_num(self, key1: int, key2: int) -> None:
        """Merge two cell groups into one after their wall has been opened.

        The coordinates of the group with the larger key are moved into
        the group with the smaller key, and the larger key is removed
        from ``self._cell``.

        Args:
            key1: Key of the first cell group.
            key2: Key of the second cell group.
        """
        if key1 < key2:
            self._cell[key1].extend(self._cell[key2])
            del self._cell[key2]
        else:
            self._cell[key2].extend(self._cell[key1])
            del self._cell[key1]

    def is_a_maze(self) -> bool:
        """Check whether all cells have been merged into a single group.

        Returns:
            True if exactly one cell group remains in ``self._cell``,
            meaning the maze carving is complete; False otherwise.
        """
        if len(self._cell) == 1:
            return True
        else:
            return False

    def save_a_maze(self) -> None:
        """Serialize the maze to the configured output file and stdout.

        Writes the hexadecimal wall grid, followed by a blank line, the
        entry coordinates, the exit coordinates, and the solution path
        computed by :meth:`solve_bfs`. The same content is printed to
        stdout. Errors encountered while writing the output file are
        caught and printed rather than raised.
        """
        output: str = ""
        for y in range(self._height):
            for x in range(self._width):
                output = output+format(self._birdview_16[(x, y)], "X")
            output = output+"\n"
        output = output+"\n"
        output = output+f"{self._entry[0]},{self._entry[1]}\n"
        output = output+f"{self._exit[0]},{self._exit[1]}\n"
        output = output+f"{"".join(self._ans)}\n"
        print(output, end="")
        try:
            with open(self._outputfile, "w") as fd:
                fd.write(output)
        except Exception as e:
            print(e)

    def solve_bfs(self) -> None:
        """Compute the shortest path from entry to exit via breadth-first search.

        Explores the maze from ``self._entry`` following open walls and
        records, for each visited cell, the direction letter used to
        reach it. The resulting path is stored as a list of direction
        letters (``N``, ``E``, ``S``, ``W``) in ``self._ans``.

        Raises:
            ConfigErorr: If the exit is unreachable from the entry.
        """
        # 1=N, 2=E, 4=S, 8=W
        directions: dict[int, tuple[str, tuple[int, int]]] = {
            1: ("N", (0, -1)),
            2: ("E", (1, 0)),
            4: ("S", (0, 1)),
            8: ("W", (-1, 0)),
        }

        queue: deque[tuple[int, int]] = deque([self._entry])
        visited: set[tuple[int, int]] = {self._entry}
        came_from: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}

        while queue:
            current: tuple[int, int] = queue.popleft()
            if current == self._exit:
                break
            walls: int = self._birdview_16[current]
            for bit, (letter, (dx, dy)) in directions.items():
                if walls & bit:
                    continue
                neighbor: tuple[int, int] = (current[0] + dx, current[1] + dy)
                if neighbor not in visited:
                    visited.add(neighbor)
                    came_from[neighbor] = (current, letter)
                    queue.append(neighbor)

        if self._exit != self._entry and self._exit not in came_from:
            raise ConfigErorr

        node: tuple[int, int] = self._exit
        while node != self._entry:
            previous, letter = came_from[node]
            self._ans.append(letter)
            node = previous
        self._ans.reverse()


if __name__ == "__main__":
    def main() -> None:
        """Run the maze generator end-to-end from the CLI.

        Loads the configuration, initializes the grid, repeatedly merges
        random adjacent cell pairs until a single connected maze remains,
        solves it with BFS, and saves the result. Any exception raised
        during the process is caught and printed instead of propagating.
        """
        tst_gen: MazeGenerator = MazeGenerator()
        try:
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
            tst_gen.solve_bfs()
            tst_gen.save_a_maze()
        except Exception as e:
            print(e)

    main()
