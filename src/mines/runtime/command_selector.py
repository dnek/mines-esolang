from mines.player.board import CellDigit
from mines.player.operation import (
    ClickOperation,
    ClickResult,
    NoOperation,
    Operation,
    RestartOperation,
    SwitchOperation,
)
from mines.player.player import Player
from mines.runtime.command import (
    ADD_COMMAND,
    DIV_COMMAND,
    DUP_COMMAND,
    IN_C_COMMAND,
    IN_N_COMMAND,
    MOD_COMMAND,
    MUL_COMMAND,
    NOOP_COMMAND,
    NOT_COMMAND,
    OUT_C_COMMAND,
    OUT_N_COMMAND,
    PERFORM_L_COMMAND,
    PERFORM_R_COMMAND,
    POP_COMMAND,
    POSITIVE_COMMAND,
    PUSH_COUNT_COMMAND,
    PUSH_N_COMMAND,
    PUSH_SUM_COMMAND,
    RESET_L_COMMAND,
    RESET_R_COMMAND,
    REVERSE_COMMAND,
    ROLL_COMMAND,
    SKIP_COMMAND,
    SUB_COMMAND,
    SWAP_COMMAND,
    Command,
)


class CommandSelectorInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in command selector: {message}")


def __select_click_on_opened_command(
    click_result: ClickResult,
    clicked_digit: CellDigit,
) -> Command:
    if click_result.open_result is not None:
        if click_result.open_result == "over":
            return RESET_R_COMMAND
        return PUSH_SUM_COMMAND

    mapping: dict[CellDigit, Command] = (
        {
            0: POP_COMMAND,
            1: POSITIVE_COMMAND,
            2: DUP_COMMAND,
            3: ADD_COMMAND,
            4: SUB_COMMAND,
            5: MUL_COMMAND,
            6: DIV_COMMAND,
            7: MOD_COMMAND,
            8: PERFORM_L_COMMAND,
        }
        if click_result.is_left_click
        else {
            0: PUSH_N_COMMAND,
            1: NOT_COMMAND,
            2: ROLL_COMMAND,
            3: IN_N_COMMAND,
            4: IN_C_COMMAND,
            5: OUT_N_COMMAND,
            6: OUT_C_COMMAND,
            7: SKIP_COMMAND,
            8: PERFORM_R_COMMAND,
        }
    )
    command = mapping.get(clicked_digit)
    if command is None:
        message = f"clicked digit: {clicked_digit} is invalid."
        raise CommandSelectorInternalError(message)
    return command


def __select_click_command(
    click_operation: ClickOperation,
    player: Player,
) -> Command:
    click_result = player.get_last_click_result()
    if click_result is None:
        message = "Click result is none."
        raise CommandSelectorInternalError(message)

    clicked_digit = player.get_cell_digit(click_operation.cell)

    match click_result.previous_cell_state:
        case "unopened":
            if click_result.is_left_click:
                match clicked_digit:
                    case 0:
                        return PUSH_COUNT_COMMAND
                    case 9:
                        return RESET_L_COMMAND
                    case _:
                        return PUSH_N_COMMAND
            return SWAP_COMMAND
        case "flagged":
            return NOOP_COMMAND if click_result.is_left_click else SWAP_COMMAND
        case "opened":
            return __select_click_on_opened_command(click_result, clicked_digit)


def select_command(operation: Operation, player: Player) -> Command:
    match operation:
        case NoOperation() | RestartOperation():
            return NOOP_COMMAND
        case SwitchOperation():
            return REVERSE_COMMAND
        case ClickOperation():
            return __select_click_command(operation, player)
