from typing import Literal, NamedTuple

from mines.player.board import Cell, CellState


class ClickOperation(NamedTuple):
    cell: Cell
    is_left_button: bool


class SwitchOperation:
    __slots__ = ()


class RestartOperation:
    __slots__ = ()


class NoOperation:
    __slots__ = ()


Operation = ClickOperation | SwitchOperation | RestartOperation | NoOperation

OpenResult = list[Cell] | Literal["over"]


class ClickResult(NamedTuple):
    previous_cell_state: CellState
    is_left_click: bool
    clicked_cell: Cell
    open_result: OpenResult | None
