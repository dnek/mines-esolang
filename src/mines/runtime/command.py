from collections.abc import Callable
from typing import NamedTuple

from mines.player.board import Cell
from mines.player.operation import ClickOperation, ClickResult, RestartOperation
from mines.runtime.command_type import CommandErrorType, CommandType
from mines.runtime.runtime_state import RuntimeState


class Command(NamedTuple):
    name: CommandType
    execute: Callable[[RuntimeState], None]
    validate: Callable[[RuntimeState], CommandErrorType | None] | None


class CommandInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in command: {message}")


def __get_click_result(runtime_state: RuntimeState) -> ClickResult:
    click_result = runtime_state.player.get_last_click_result()
    if click_result is None:
        message = "Click result is none."
        raise CommandInternalError(message)
    return click_result


def __run_push_n(runtime_state: RuntimeState) -> None:
    click_result = __get_click_result(runtime_state)
    runtime_state.stack.push(
        runtime_state.player.get_cell_digit(click_result.clicked_cell),
    )


def __get_opened_cells(click_result: ClickResult) -> list[Cell]:
    if not isinstance(click_result.open_result, list):
        message = f"Open result: {click_result.open_result} is not a list."
        raise CommandInternalError(message)
    return click_result.open_result


def __run_push_count(runtime_state: RuntimeState) -> None:
    click_result = __get_click_result(runtime_state)
    runtime_state.stack.push(len(__get_opened_cells(click_result)))


def __run_push_sum(runtime_state: RuntimeState) -> None:
    click_result = __get_click_result(runtime_state)
    opened_cells = __get_opened_cells(click_result)
    sum_value = sum(runtime_state.player.get_cell_digit(cell) for cell in opened_cells)
    runtime_state.stack.push(sum_value)


def __get_pop_validator(
    pop_count: int,
) -> Callable[[RuntimeState], CommandErrorType | None]:
    def validate_push(runtime_state: RuntimeState) -> CommandErrorType | None:
        if len(runtime_state.stack) < pop_count:
            return "StackUnderflowError"
        return None

    return validate_push


def __push_with_constant_pops(
    runtime_state: RuntimeState,
    pop_count: int,
    func: Callable[[list[int]], int],
) -> None:
    value = func(runtime_state.stack.get_pops(pop_count))
    runtime_state.stack.push(value)


def __run_pop(runtime_state: RuntimeState) -> None:
    runtime_state.stack.get_pops(1)


def __run_positive(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 1, lambda pops: 1 if pops[0] > 0 else 0)


def __run_dup(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(1)
    runtime_state.stack.push(pops[0], pops[0])


def __run_add(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 2, lambda pops: pops[1] + pops[0])


def __run_sub(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 2, lambda pops: pops[1] - pops[0])


def __run_mul(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 2, lambda pops: pops[1] * pops[0])


def __validate_div(runtime_state: RuntimeState) -> CommandErrorType | None:
    if constant_pop_error := __get_pop_validator(2)(runtime_state):
        return constant_pop_error

    if runtime_state.stack.peek(0) == 0:
        return "ZeroDivisionError"

    return None


def __run_div(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 2, lambda pops: pops[1] // pops[0])


def __run_mod(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 2, lambda pops: pops[1] % pops[0])


def __run_not(runtime_state: RuntimeState) -> None:
    __push_with_constant_pops(runtime_state, 1, lambda pops: 1 if pops[0] == 0 else 0)


def __validate_roll(runtime_state: RuntimeState) -> CommandErrorType | None:
    if constant_pop_error := __get_pop_validator(2)(runtime_state):
        return constant_pop_error

    if len(runtime_state.stack) < 2 + abs(runtime_state.stack.peek(1)):
        return "StackUnderflowError"

    return None


def __run_roll(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(2)
    runtime_state.stack.roll(pops[1], pops[0])


def __validate_in_n(runtime_state: RuntimeState) -> CommandErrorType | None:
    if not runtime_state.input_buffer.validate_request_integer():
        return "InputMismatchError"

    return None


def __validate_in_c(runtime_state: RuntimeState) -> CommandErrorType | None:
    if not runtime_state.input_buffer.validate_request_char():
        return "InputMismatchError"

    return None


def __validate_out_c(runtime_state: RuntimeState) -> CommandErrorType | None:
    if constant_pop_error := __get_pop_validator(1)(runtime_state):
        return constant_pop_error

    if not runtime_state.output_buffer.validate_write_as_char(
        runtime_state.stack.peek(0),
    ):
        return "UnicodeRangeError"

    return None


def __run_in_n(runtime_state: RuntimeState) -> None:
    runtime_state.stack.push(runtime_state.input_buffer.request_integer())


def __run_in_c(runtime_state: RuntimeState) -> None:
    runtime_state.stack.push(runtime_state.input_buffer.request_char())


def __run_out_n(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(1)
    runtime_state.output_buffer.write_as_integer(pops[0])


def __run_out_c(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(1)
    runtime_state.output_buffer.write_as_char(pops[0])


def __run_skip(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(1)
    runtime_state.operation_pointer.advance(pops[0])


def __get_click_operation(
    runtime_state: RuntimeState,
    *,
    is_left_button: bool,
) -> ClickOperation:
    pops = runtime_state.stack.get_pops(2)
    return ClickOperation(
        runtime_state.player.get_board_size().get_wrapped_cell(
            unwrapped_column_index=pops[1],
            unwrapped_row_index=pops[0],
        ),
        is_left_button,
    )


def __run_perform_l(runtime_state: RuntimeState) -> None:
    click_operation = __get_click_operation(runtime_state, is_left_button=True)
    runtime_state.operation_queue.append(click_operation)


def __run_perform_r(runtime_state: RuntimeState) -> None:
    click_operation = __get_click_operation(runtime_state, is_left_button=False)
    runtime_state.operation_queue.append(click_operation)


def __run_reset_l(runtime_state: RuntimeState) -> None:
    runtime_state.operation_queue.append(RestartOperation())


def __run_reset_r(runtime_state: RuntimeState) -> None:
    runtime_state.stack.clear()
    runtime_state.operation_queue.append(RestartOperation())


def __run_swap(runtime_state: RuntimeState) -> None:
    pops = runtime_state.stack.get_pops(2)
    runtime_state.stack.push(pops[0], pops[1])


def __run_reverse(runtime_state: RuntimeState) -> None:
    runtime_state.stack.reverse()


def __run_noop(_: RuntimeState) -> None:
    pass


PUSH_N_COMMAND = Command("push(n)", __run_push_n, None)
PUSH_COUNT_COMMAND = Command("push(count)", __run_push_count, None)
PUSH_SUM_COMMAND = Command("push(sum)", __run_push_sum, None)

POP_COMMAND = Command("pop", __run_pop, __get_pop_validator(1))
POSITIVE_COMMAND = Command("positive", __run_positive, __get_pop_validator(1))
DUP_COMMAND = Command("dup", __run_dup, __get_pop_validator(1))

ADD_COMMAND = Command("add", __run_add, __get_pop_validator(2))
SUB_COMMAND = Command("sub", __run_sub, __get_pop_validator(2))
MUL_COMMAND = Command("mul", __run_mul, __get_pop_validator(2))
DIV_COMMAND = Command("div", __run_div, __validate_div)
MOD_COMMAND = Command("mod", __run_mod, __validate_div)

NOT_COMMAND = Command("not", __run_not, __get_pop_validator(1))
ROLL_COMMAND = Command("roll", __run_roll, __validate_roll)

IN_N_COMMAND = Command("in(n)", __run_in_n, __validate_in_n)
IN_C_COMMAND = Command("in(c)", __run_in_c, __validate_in_c)
OUT_N_COMMAND = Command("out(n)", __run_out_n, __get_pop_validator(1))
OUT_C_COMMAND = Command("out(c)", __run_out_c, __validate_out_c)

SKIP_COMMAND = Command("skip", __run_skip, __get_pop_validator(1))
PERFORM_L_COMMAND = Command("perform(l)", __run_perform_l, __get_pop_validator(2))
PERFORM_R_COMMAND = Command("perform(r)", __run_perform_r, __get_pop_validator(2))
RESET_L_COMMAND = Command("reset(l)", __run_reset_l, None)
RESET_R_COMMAND = Command("reset(r)", __run_reset_r, None)

SWAP_COMMAND = Command("swap", __run_swap, __get_pop_validator(2))
REVERSE_COMMAND = Command("reverse", __run_reverse, None)
NOOP_COMMAND = Command("noop", __run_noop, None)
