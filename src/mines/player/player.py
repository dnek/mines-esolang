from collections import deque
from collections.abc import Iterable

from mines.player.board import (
    CELL_DIGIT_MINE,
    BoardSize,
    BoardValues,
    Cell,
    CellDigit,
)
from mines.player.operation import (
    ClickOperation,
    ClickResult,
    NoOperation,
    OpenResult,
    Operation,
    RestartOperation,
    SwitchOperation,
)
from mines.player.player_state import PlayerState


class Player:
    __board_size: BoardSize
    __cell_digits: BoardValues[CellDigit]
    __mine_number: int

    __player_state: PlayerState
    __rest_mine_count: int
    __rest_safe_count: int
    __last_click_result: ClickResult | None

    def __init__(
        self,
        cell_digits: BoardValues[CellDigit],
    ) -> None:
        self.__board_size = cell_digits.get_board_size()
        self.__cell_digits = cell_digits
        self.__mine_number = list(cell_digits.iterate_values()).count(9)

        self.__player_state = PlayerState(
            game_status="playing",
            cell_states=BoardValues(self.__board_size, lambda _: "unopened"),
            flag_mode=False,
        )
        self.__rest_mine_count = self.__mine_number
        self.__rest_safe_count = self.get_initial_safe_count()
        self.__last_click_result = None

    def __open_safe_cells(self, cells: Iterable[Cell]) -> list[Cell]:
        opened_cells: list[Cell] = []
        queue = deque(cells)

        while len(queue) > 0:
            cell = queue.popleft()

            if self.__player_state.cell_states.get(cell) != "unopened":
                continue

            self.__player_state.cell_states.set(cell, "opened")
            self.__rest_safe_count -= 1
            opened_cells.append(cell)

            if self.__cell_digits.get(cell) == 0:
                for next_cell in self.__board_size.iterate_adjacent_cells(cell):
                    queue.append(next_cell)

        if self.__rest_safe_count == 0:
            self.__player_state.game_status = "cleared"

        return opened_cells

    def __open_cells_or_over(self, cells: Iterable[Cell]) -> OpenResult:
        if any(self.__cell_digits.get(cell) == CELL_DIGIT_MINE for cell in cells):
            self.__player_state.game_status = "over"
            return "over"

        return self.__open_safe_cells(cells)

    def __get_chord_cells(self, cell: Cell) -> list[Cell]:
        unopened_cells: list[Cell] = []
        flagged_cells: list[Cell] = []
        for next_cell in self.__board_size.iterate_adjacent_cells(cell):
            match self.__player_state.cell_states.get(next_cell):
                case "unopened":
                    unopened_cells.append(next_cell)
                case "flagged":
                    flagged_cells.append(next_cell)
                case "opened":
                    pass

        if len(flagged_cells) == self.__cell_digits.get(cell):
            return unopened_cells

        return []

    def __perform_click(
        self,
        operation: ClickOperation,
    ) -> None:
        cell = operation.cell
        cell_state = self.__player_state.cell_states.get(cell)
        is_left_click = operation.is_left_button ^ self.__player_state.flag_mode
        open_result: OpenResult | None = None

        match cell_state:
            case "unopened":
                if is_left_click:
                    open_result = self.__open_cells_or_over([cell])
                else:
                    self.__player_state.cell_states.set(cell, "flagged")
                    self.__rest_mine_count -= 1
            case "flagged":
                if not is_left_click:
                    self.__player_state.cell_states.set(cell, "unopened")
                    self.__rest_mine_count += 1
            case "opened":
                if not is_left_click:
                    chord_cells = self.__get_chord_cells(cell)
                    if len(chord_cells) > 0:
                        open_result = self.__open_cells_or_over(chord_cells)

        self.__last_click_result = ClickResult(
            previous_cell_state=cell_state,
            is_left_click=is_left_click,
            clicked_cell=cell,
            open_result=open_result,
        )

    def __perform_switch(self) -> None:
        self.__player_state.flag_mode ^= True

    def __perform_restart(self) -> None:
        for cell in self.__board_size.iterate_board_cells():
            self.__player_state.cell_states.set(cell, "unopened")
        self.__rest_mine_count = self.__mine_number
        self.__rest_safe_count = self.get_initial_safe_count()
        self.__player_state.game_status = "playing"

    def perform_operation(self, operation: Operation) -> None:
        self.__last_click_result = None

        match operation:
            case ClickOperation():
                self.__perform_click(operation)
            case SwitchOperation():
                self.__perform_switch()
            case RestartOperation():
                self.__perform_restart()
            case NoOperation():
                pass

    def get_board_size(self) -> BoardSize:
        return self.__board_size

    def get_cell_digit(self, cell: Cell) -> CellDigit:
        return self.__cell_digits.get(cell)

    def get_mine_number(self) -> int:
        return self.__mine_number

    def get_initial_safe_count(self) -> int:
        board_size = self.__board_size
        return board_size.width * board_size.height - self.__mine_number

    def get_player_state(self) -> PlayerState:
        return self.__player_state

    def get_rest_mine_count(self) -> int:
        return self.__rest_mine_count

    def get_rest_safe_count(self) -> int:
        return self.__rest_safe_count

    def get_last_click_result(self) -> ClickResult | None:
        return self.__last_click_result

    def replace_cell_digits_safely(
        self,
        cell_digits: BoardValues[CellDigit],
    ) -> bool:
        if self.__player_state.game_status != "playing":
            return False

        if cell_digits.get_board_size() != self.__board_size:
            return False

        if list(cell_digits.iterate_values()).count(9) != self.__mine_number:
            return False

        for cell in self.__board_size.iterate_board_cells():
            if self.__player_state.cell_states.get(cell) != "opened":
                continue
            if cell_digits.get(cell) != self.__cell_digits.get(cell):
                return False

        self.__cell_digits = cell_digits
        return True
