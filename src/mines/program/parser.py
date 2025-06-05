import re

from mines.player.board import (
    BoardSize,
    BoardValues,
    Cell,
    CellDigit,
    is_cell_digit,
)
from mines.player.operation import (
    ClickOperation,
    NoOperation,
    Operation,
    RestartOperation,
    SwitchOperation,
)
from mines.program.program import Program


class ParserInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in parser: {message}")


class MinesCodeSyntaxError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Syntax error in Mines code: {message}")


class IntegerSyntaxError(MinesCodeSyntaxError):
    def __init__(self, value: str) -> None:
        super().__init__(f"Number '{value}' is not a valid integer.")


class OperationSyntaxError(MinesCodeSyntaxError):
    def __init__(self, line: str) -> None:
        super().__init__(f"Operation '{line}' is inconsistent.")


class NoBoardSyntaxError(MinesCodeSyntaxError):
    def __init__(self) -> None:
        super().__init__("No board.")


class NoOperationsSyntaxError(MinesCodeSyntaxError):
    def __init__(self) -> None:
        super().__init__("No operations.")


def __parse_int(value: str) -> int:
    if not re.compile(r"^[+-]?[0-9]+$").match(value):
        raise IntegerSyntaxError(value)
    return int(value)


def __parse_click_operation(
    line: str,
    board_size: BoardSize,
    *,
    is_left_button: bool,
) -> ClickOperation | None:
    separator = "," if is_left_button else ";"
    parts = line.partition(separator)
    if parts[1] != separator:
        return None
    unwrapped_column_index_str, _, unwrapped_row_index_str = parts

    return ClickOperation(
        cell=board_size.get_wrapped_cell(
            unwrapped_column_index=__parse_int(unwrapped_column_index_str),
            unwrapped_row_index=__parse_int(unwrapped_row_index_str),
        ),
        is_left_button=is_left_button,
    )


def __parse_operation(line: str, board_size: BoardSize) -> Operation:
    match line:
        case "":
            return NoOperation()
        case "!":
            return SwitchOperation()
        case "@":
            return RestartOperation()
        case _:
            if click_operation := (
                __parse_click_operation(line, board_size, is_left_button=True)
                or __parse_click_operation(line, board_size, is_left_button=False)
            ):
                return click_operation

    raise OperationSyntaxError(line)


def parse(code: str) -> Program:
    formatted_lines = [
        (line + "#")[: line.find("#")].translate(str.maketrans("", "", " \t\v\f\r"))
        for line in code.split(sep="\n")
    ]

    header_count = next(
        (
            index
            for index in range(len(formatted_lines))
            if len(formatted_lines[index]) > 0
        ),
        len(formatted_lines),
    )

    if header_count == len(formatted_lines):
        raise NoBoardSyntaxError

    board_width = len(formatted_lines[header_count])

    board_line_re = re.compile(rf"^[.*]{{{board_width}}}$")
    board_height = (
        next(
            (
                index
                for index in range(header_count, len(formatted_lines))
                if not board_line_re.match(formatted_lines[index])
            ),
            len(formatted_lines),
        )
        - header_count
    )

    if board_width * board_height == 0:
        raise NoBoardSyntaxError

    board_size = BoardSize(width=board_width, height=board_height)

    def count_cell_digit(cell: Cell) -> CellDigit:
        cell = Cell(row_index=cell.row_index, column_index=cell.column_index)
        if formatted_lines[header_count + cell.row_index][cell.column_index] == "*":
            return 9

        mine_count = sum(
            formatted_lines[header_count + next_cell.row_index][next_cell.column_index]
            == "*"
            for next_cell in board_size.iterate_adjacent_cells(cell)
        )
        if is_cell_digit(mine_count):
            return mine_count

        message = f"mine count: {mine_count} is not a cell digit."
        raise ParserInternalError(message)

    cell_digits = BoardValues[CellDigit](board_size, count_cell_digit)

    operation_list = [
        __parse_operation(formatted_lines[index], board_size)
        for index in range(header_count + board_height, len(formatted_lines))
    ]

    if len(operation_list) == 0:
        raise NoOperationsSyntaxError

    return Program(cell_digits, operation_list)
