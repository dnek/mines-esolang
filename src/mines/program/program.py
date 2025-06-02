from typing import NamedTuple

from mines.player.board import BoardSize, BoardValues, CellNumber
from mines.player.operation import Operation


class Program(NamedTuple):
    board_size: BoardSize
    cell_numbers: BoardValues[CellNumber]
    operation_list: list[Operation]
