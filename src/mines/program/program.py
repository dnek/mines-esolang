from typing import NamedTuple

from mines.player.board import BoardValues, CellDigit
from mines.player.operation import Operation


class Program(NamedTuple):
    cell_digits: BoardValues[CellDigit]
    operation_list: list[Operation]
