from mines.player.board import CELL_DIGIT_MINE, BoardValues, Cell, CellState
from mines.player.player import Player
from mines.view.ansi import ANSI_LF, Ansi, em


class PlayerView:
    __player: Player

    def __init__(self, player: Player) -> None:
        self.__player = player

    def __get_cell_ansi(self, cell: Cell, cell_state: CellState | None = None) -> Ansi:
        player = self.__player
        is_over = player.get_player_state().game_status == "over"
        cell_digit = player.get_cell_digit(cell)
        match cell_state or player.get_player_state().cell_states.get(cell):
            case "unopened":
                raw_str = "＊" if is_over and cell_digit == CELL_DIGIT_MINE else "＿"  # noqa: RUF001
                return Ansi(raw_str, fg=0, bg=7)
            case "flagged":
                raw_str = "Ｘ" if is_over and cell_digit != CELL_DIGIT_MINE else "Ｆ"  # noqa: RUF001
                return Ansi(raw_str, fg=0, bg=7)
            case "opened":
                match cell_digit:
                    case 0:
                        return Ansi("・", faint=True)
                    case _:
                        return Ansi(chr(cell_digit + 65296))

    def get_board_info_str(self) -> str:
        player = self.__player
        board_size = player.get_board_size()
        rest_mine_count = player.get_rest_mine_count()
        mine_number = player.get_mine_number()
        rest_safe_count = player.get_rest_safe_count()
        initial_safe_count = player.get_initial_safe_count()
        flag_mode = player.get_player_state().flag_mode

        return " ".join(
            [
                f"{board_size.width}x{board_size.height}",
                f"mines: {rest_mine_count}/{mine_number}",
                f"safes: {rest_safe_count}/{initial_safe_count}",
                f"flag mode: {em('ON' if flag_mode else 'OFF')}",
            ],
        )

    def get_board_str(self, selected_cell: Cell | None = None) -> str:
        board_ansi = BoardValues[Ansi](
            self.__player.get_board_size(),
            self.__get_cell_ansi,
        )

        if selected_cell:
            board_ansi.get(selected_cell).bg = 4

        click_result = self.__player.get_last_click_result()
        if click_result:
            if isinstance(click_result.open_result, list):
                for cell in click_result.open_result:
                    board_ansi.get(cell).bg = 2

            clicked_cell = click_result.clicked_cell
            cell_state = self.__player.get_player_state().cell_states.get(clicked_cell)

            if click_result.previous_cell_state != cell_state:
                clicked_cell_bg = 5
            else:
                match click_result.open_result:
                    case None:
                        clicked_cell_bg = 3
                    case "over":
                        clicked_cell_bg = 1
                    case _:
                        clicked_cell_bg = 4
            board_ansi.get(clicked_cell).bg = clicked_cell_bg
        return board_ansi.draw(end=ANSI_LF)

    def get_click_result_str(self) -> str:
        click_result = self.__player.get_last_click_result()
        if click_result is None:
            return "--"

        click = f"{em('L' if click_result.is_left_click else 'R')}-click"

        clicked_cell = click_result.clicked_cell
        previous_cell_state = click_result.previous_cell_state
        cell_state = self.__player.get_player_state().cell_states.get(clicked_cell)

        previous_cell_ansi = self.__get_cell_ansi(clicked_cell, previous_cell_state)
        current_cell_ansi = self.__get_cell_ansi(clicked_cell)
        diff_str = f"{click} at {previous_cell_ansi} -> {current_cell_ansi}"

        match click_result.open_result:
            case None:
                if previous_cell_state != cell_state:
                    description_str = f"changed to {em(cell_state)}"
                else:
                    description_str = "for nothing"
            case "over":
                description_str = f"caused {em('Game Over')}"
            case _:
                opened_count_str = em(str(len(click_result.open_result)))
                description_str = f"opened {opened_count_str} cells"
        return f"{diff_str} {description_str}"
