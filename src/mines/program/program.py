from typing import NamedTuple

from mines.player.board import BoardSize, BoardValues, CellDigit
from mines.player.operation import Operation


class Program(NamedTuple):
    board_size: BoardSize
    cell_digits: BoardValues[CellDigit]
    operation_list: list[Operation]
