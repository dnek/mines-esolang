from dataclasses import dataclass

from mines.minesweeper.board import Cell


@dataclass(frozen=True)
class ClickOperation:
    is_left_button: bool
    cell: Cell


@dataclass(frozen=True)
class SwitchOperation:
    pass


@dataclass(frozen=True)
class NoOperation:
    pass


Operation = ClickOperation | SwitchOperation | NoOperation
