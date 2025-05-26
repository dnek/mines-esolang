from collections import deque
from dataclasses import dataclass
from typing import Iterable, Literal

from mines.minesweeper.board import BoardSize, BoardValues, Cell, CellNumber, CellState
from mines.minesweeper.operation import ClickOperation

OpenResult = list[CellNumber] | Literal["over"]


@dataclass(frozen=True)
class ClickResult:
    previous_cell_state: CellState
    is_left_click: bool
    clicked_number: CellNumber
    open_result: OpenResult | None


class Player:
    __board_size: BoardSize
    cell_numbers: BoardValues[CellNumber]
    cell_states: BoardValues[CellState]
    __initial_safe_count: int
    __rest_safe_count: int
    flag_mode: bool

    def __init__(
        self, board_size: BoardSize, cell_numbers: BoardValues[CellNumber]
    ) -> None:
        self.__board_size = board_size
        self.cell_numbers = cell_numbers

        self.cell_states = BoardValues(board_size, "unopened")

        mine_count = list(cell_numbers.iterate_values()).count(9)
        self.__initial_safe_count = board_size.width * board_size.height - mine_count
        self.__rest_safe_count = self.__initial_safe_count
        self.flag_mode = False

    def __open_safe_cells(self, cells: Iterable[Cell]) -> Iterable[Cell]:
        queue = deque(cells)

        while len(queue) > 0:
            cell = queue.popleft()

            if self.cell_states.get(cell) != "unopened":
                continue

            self.cell_states.set(cell, "opened")
            self.__rest_safe_count -= 1
            yield cell

            if self.cell_numbers.get(cell) == 0:
                for next_cell in self.__board_size.iterate_surrounding_cells(cell):
                    queue.append(next_cell)

    def __open_cells_or_over(self, cells: Iterable[Cell]) -> OpenResult:
        if any(self.cell_numbers.get(cell) == 9 for cell in cells):
            for cell in self.__board_size.iterate_board_cells():
                self.cell_states.set(cell, "unopened")
                self.__rest_safe_count = self.__initial_safe_count
            return "over"
        else:
            return [
                self.cell_numbers.get(cell) for cell in self.__open_safe_cells(cells)
            ]

    def __get_chord_cells(self, cell: Cell) -> list[Cell]:
        unopened_cells: list[Cell] = []
        flagged_cells: list[Cell] = []
        for next_cell in self.__board_size.iterate_surrounding_cells(cell):
            match self.cell_states.get(next_cell):
                case "unopened":
                    unopened_cells.append(next_cell)
                case "flagged":
                    flagged_cells.append(next_cell)

        if len(flagged_cells) == self.cell_numbers.get(cell):
            return unopened_cells

        return []

    def perform_click(self, operation: ClickOperation) -> ClickResult:
        cell = operation.cell
        cell_state = self.cell_states.get(cell)
        is_left_click = operation.is_left_button ^ self.flag_mode
        open_result: OpenResult | None = None

        match cell_state:
            case "unopened":
                if is_left_click:
                    open_result = self.__open_cells_or_over([cell])
                else:
                    self.cell_states.set(cell, "flagged")
            case "flagged":
                if not is_left_click:
                    self.cell_states.set(cell, "unopened")
            case "opened":
                if not is_left_click:
                    chord_cells = self.__get_chord_cells(cell)
                    if len(chord_cells) > 0:
                        open_result = self.__open_cells_or_over(chord_cells)

        return ClickResult(
            previous_cell_state=cell_state,
            is_left_click=is_left_click,
            clicked_number=self.cell_numbers.get(cell),
            open_result=open_result,
        )

    def perform_switch(self):
        self.flag_mode ^= True

    def is_all_safe_cells_opened(self):
        return self.__rest_safe_count == 0
