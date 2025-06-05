import sys
from functools import partial
from random import shuffle
from sys import stderr

from mines.player.board import (
    CELL_DIGIT_MINE,
    BoardSize,
    BoardValues,
    Cell,
    CellDigit,
    is_cell_digit,
)
from mines.player.operation import (
    ClickOperation,
    NoOperation,
    RestartOperation,
    SwitchOperation,
)
from mines.player.player import Player
from mines.view.ansi import Ansi
from mines.view.cli_frame_drawer import CliFrameDrawer
from mines.view.player_view import PlayerView
from mines.view.prompt import Prompt


class GameInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in game: {message}")


MinePattern = int | BoardValues[CellDigit]


class Game:
    __level_name: str
    __board_size: BoardSize
    __mine_pattern: MinePattern

    __player: Player
    __selected_cell: Cell

    def __init__(
        self,
        level_name: str,
        board_size: BoardSize,
        mine_pattern: MinePattern,
    ) -> None:
        self.__level_name = level_name
        self.__board_size = board_size
        self.__mine_pattern = mine_pattern
        if isinstance(mine_pattern, int):
            cell_digits = self.__get_random_cell_digits(None)
            self.__player = Player(cell_digits)
        else:
            self.__player = Player(mine_pattern)
        self.__selected_cell = Cell(0, 0)

    def __draw(self) -> None:
        player_view = PlayerView(self.__player)

        cli_frame_drawer = CliFrameDrawer()
        cli_frame_drawer.add_line(self.__level_name, "level")
        cli_frame_drawer.add_line(player_view.get_board_info_str())
        cli_frame_drawer.add_line("")
        cli_frame_drawer.add_line(player_view.get_board_str(self.__selected_cell))
        cli_frame_drawer.add_line("")

        cli_frame_drawer.draw_frame()

    def __get_random_cell_digits(
        self,
        start_cell: Cell | None,
    ) -> BoardValues[CellDigit]:
        board_size = self.__board_size
        excluded_cells: list[Cell] = []
        if start_cell:
            excluded_cells.append(start_cell)
            excluded_cells.extend(board_size.iterate_adjacent_cells(start_cell))

        mine_candidates = [
            cell
            for cell in board_size.iterate_board_cells()
            if cell not in excluded_cells
        ]
        shuffle(mine_candidates)

        cell_digits = BoardValues[CellDigit](board_size, lambda _: 0)

        if not isinstance(self.__mine_pattern, int):
            message = "Mine pattern is fixed."
            raise GameInternalError(message)

        for _ in range(self.__mine_pattern):
            cell = mine_candidates.pop()
            cell_digits.set(cell, 9)
            for next_cell in board_size.iterate_adjacent_cells(cell):
                old_digit = cell_digits.get(next_cell)
                if old_digit == CELL_DIGIT_MINE:
                    continue
                new_digit = old_digit + 1
                if not is_cell_digit(new_digit):
                    message = f"{new_digit} is not a cell digit."
                    raise GameInternalError(message)
                cell_digits.set(next_cell, new_digit)

        return cell_digits

    def __set_safe_cell_digits_for_first_open(self, *, is_z_key: bool) -> None:
        if not isinstance(self.__mine_pattern, int):
            return

        player = self.__player
        if is_z_key == player.get_player_state().flag_mode:
            return

        if player.get_rest_safe_count() != player.get_initial_safe_count():
            return

        cell_digits = self.__get_random_cell_digits(self.__selected_cell)
        result = player.replace_cell_digits_safely(cell_digits)

        if not result:
            message = "Cell digits was not replaced safely."
            raise GameInternalError(message)

    def __click(self, *, is_z_key: bool) -> None:
        self.__set_safe_cell_digits_for_first_open(is_z_key=is_z_key)

        operation = ClickOperation(
            self.__selected_cell,
            is_left_button=is_z_key,
        )
        self.__player.perform_operation(operation)

    def __switch(self) -> None:
        self.__player.perform_operation(SwitchOperation())

    def __move(self, dx: int, dy: int) -> None:
        old_cell = self.__selected_cell
        old_column_index, old_row_index = old_cell
        new_cell = Cell(old_column_index + dx, old_row_index + dy)
        if new_cell not in self.__board_size.iterate_adjacent_cells(old_cell):
            return
        self.__selected_cell = new_cell
        self.__player.perform_operation(NoOperation())

    def __show_playing_prompt(self) -> None:
        prompt = Prompt()

        z_key_desc = "open"
        x_key_desc = "flag/unflag/chord"
        if self.__player.get_player_state().flag_mode:
            z_key_desc, x_key_desc = x_key_desc, z_key_desc

        prompt.add("z", lambda: self.__click(is_z_key=True), f"[z] {z_key_desc}")

        prompt.add("x", lambda: self.__click(is_z_key=False), f"[x] {x_key_desc}")
        prompt.add("f", self.__switch, "[f] switch flag mode")

        prompt.add_desc("[wasd]/[↑←↓→] move")
        move_params: tuple[tuple[tuple[str, str], int, int], ...] = (
            (("w", "UP"), 0, -1),
            (("a", "LEFT"), -1, 0),
            (("s", "DOWN"), 0, 1),
            (("d", "RIGHT"), 1, 0),
        )
        for keys, dx, dy in move_params:
            move = partial(self.__move, dx, dy)
            prompt.add(keys, move, None)

        prompt.add("q", lambda: sys.exit(0), "[q] quit\n")

        prompt.show()

    def __new_game(self) -> None:
        self.__player.perform_operation(RestartOperation())

    def __show_over_prompt(self) -> None:
        prompt = Prompt()

        prompt.add("n", self.__new_game, "[n] new game")

        prompt.add("q", lambda: sys.exit(0), "[q] quit\n")

        prompt.show()

    def __step(self) -> None:
        self.__draw()

        match self.__player.get_player_state().game_status:
            case "playing":
                self.__show_playing_prompt()
            case "over":
                stderr.write(str(Ansi("game over!\n", fg=1)))
                stderr.flush()
                self.__show_over_prompt()
            case "cleared":
                stderr.write(str(Ansi("game cleared!\n", fg=2)))
                stderr.flush()
                self.__show_over_prompt()

    def run(self) -> None:
        while True:
            self.__step()
