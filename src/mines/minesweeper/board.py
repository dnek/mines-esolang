from dataclasses import dataclass
from typing import Iterable, Literal, TypeIs


@dataclass(frozen=True)
class Cell:
    column_index: int
    row_index: int


@dataclass(frozen=True)
class BoardSize:
    width: int
    height: int

    def get_wrapped_cell(
        self, unwrapped_column_index: int, unwrapped_row_index: int
    ) -> Cell:
        return Cell(
            column_index=unwrapped_column_index % self.width,
            row_index=unwrapped_row_index % self.height,
        )

    def iterate_board_cells(self) -> Iterable[Cell]:
        for column_index in range(self.width):
            for row_index in range(self.height):
                yield Cell(column_index=column_index, row_index=row_index)

    def iterate_surrounding_cells(self, cell: Cell) -> Iterable[Cell]:
        COLUMN_DIFFS = (-1, -1, -1, 0, 0, 1, 1, 1)
        ROW_DIFFS = (-1, 0, 1, -1, 1, -1, 0, 1)
        for d_id in range(8):
            next_column_index = cell.column_index + COLUMN_DIFFS[d_id]
            next_row_index = cell.row_index + ROW_DIFFS[d_id]
            if (
                0 <= next_column_index < self.width
                and 0 <= next_row_index < self.height
            ):
                yield Cell(column_index=next_column_index, row_index=next_row_index)


class BoardValues[T]:
    __board_size: BoardSize
    __values: list[list[T]]

    def __init__(self, board_size: BoardSize, value: T) -> None:
        self.__board_size = board_size
        self.__values = [
            [value for _ in range(board_size.width)] for _ in range(board_size.height)
        ]

    def get(self, cell: Cell) -> T:
        return self.__values[cell.row_index][cell.column_index]

    def set(self, cell: Cell, value: T) -> None:
        self.__values[cell.row_index][cell.column_index] = value

    def iterate_values(self) -> Iterable[T]:
        for row_index in range(self.__board_size.height):
            for column_index in range(self.__board_size.width):
                yield self.__values[row_index][column_index]


CellState = Literal["unopened", "flagged", "opened"]

CellNumber = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def is_cell_number(value: int) -> TypeIs[CellNumber]:
    return 0 <= value <= 9
