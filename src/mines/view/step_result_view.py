from mines.player.operation import (
    ClickOperation,
    NoOperation,
    RestartOperation,
    SwitchOperation,
)
from mines.player.player import Player
from mines.runtime.runner import StepResult
from mines.view.ansi import em


class StepResultViewInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in step result view: {message}")


class StepResultView:
    __player: Player
    __step_result: StepResult

    def __init__(self, player: Player, step_result: StepResult) -> None:
        self.__player = player
        self.__step_result = step_result

    def get_operation_str(self) -> str:
        operation = self.__step_result.operation
        match operation:
            case NoOperation():
                return "no operation"
            case SwitchOperation():
                player_state = self.__player.get_player_state()
                flag_mode_str = em("ON" if player_state.flag_mode else "OFF")
                return f"switch flag mode to {flag_mode_str}"
            case RestartOperation():
                return "restart"
            case ClickOperation():
                click_result = self.__player.get_last_click_result()
                if click_result is None:
                    message = "Click result is none."
                    raise StepResultViewInternalError(message)
                button = f"{em('L' if operation.is_left_button else 'R')}-button"
                return f"{button} at {operation.cell}"

    def get_command_str(self) -> str:
        command_type = self.__step_result.command_type
        command_error_type = self.__step_result.command_error_type
        if command_error_type:
            return f"{command_type} with {em(command_error_type)}"
        return command_type
