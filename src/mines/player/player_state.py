from dataclasses import dataclass
from typing import Literal

from mines.player.board import BoardValues, CellState

GameStatus = Literal["playing", "cleared", "over"]


@dataclass
class PlayerState:
    game_status: GameStatus
    cell_states: BoardValues[CellState]
    flag_mode: bool
