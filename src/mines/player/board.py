from collections.abc import Callable, Iterable
from typing import Literal, NamedTuple, TypeIs


class Cell(NamedTuple):
    column_index: int
    row_index: int

    def __str__(self) -> str:
        return f"({self.column_index}, {self.row_index})"


ADJACENT_COLUMN_DIFFS = (-1, -1, -1, 0, 0, 1, 1, 1)
ADJACENT_ROW_DIFFS = (-1, 0, 1, -1, 1, -1, 0, 1)


class BoardSize(NamedTuple):
    width: int
    height: int

    def get_wrapped_cell(
        self,
        unwrapped_column_index: int,
        unwrapped_row_index: int,
    ) -> Cell:
        return Cell(
            column_index=unwrapped_column_index % self.width,
            row_index=unwrapped_row_index % self.height,
        )

    def iterate_board_cells(self) -> Iterable[Cell]:
        for column_index in range(self.width):
            for row_index in range(self.height):
                yield Cell(column_index=column_index, row_index=row_index)

    def iterate_adjacent_cells(self, cell: Cell) -> Iterable[Cell]:
        for d_id in range(8):
            next_column_index = cell.column_index + ADJACENT_COLUMN_DIFFS[d_id]
            next_row_index = cell.row_index + ADJACENT_ROW_DIFFS[d_id]
            if (
                0 <= next_column_index < self.width
                and 0 <= next_row_index < self.height
            ):
                yield Cell(column_index=next_column_index, row_index=next_row_index)


class BoardValues[T]:
    __board_size: BoardSize
    __values: list[list[T]]

    def __init__(self, board_size: BoardSize, item_fn: Callable[[Cell], T]) -> None:
        self.__board_size = board_size
        self.__values = [
            [
                item_fn(Cell(column_index=column_index, row_index=row_index))
                for column_index in range(board_size.width)
            ]
            for row_index in range(board_size.height)
        ]

    def get_board_size(self) -> BoardSize:
        return self.__board_size

    def get(self, cell: Cell) -> T:
        return self.__values[cell.row_index][cell.column_index]

    def set(self, cell: Cell, value: T) -> None:
        self.__values[cell.row_index][cell.column_index] = value

    def iterate_values(self) -> Iterable[T]:
        for row_index in range(self.__board_size.height):
            for column_index in range(self.__board_size.width):
                yield self.__values[row_index][column_index]

    def draw(self, sep: str = "", end: str = "\n") -> str:
        return end.join(
            [
                sep.join(
                    [
                        str(self.__values[row_index][column_index])
                        for column_index in range(self.__board_size.width)
                    ],
                )
                for row_index in range(self.__board_size.height)
            ],
        )


CellState = Literal["unopened", "flagged", "opened"]

CellDigit = Literal[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

CELL_DIGIT_MINE = 9


def is_cell_digit(value: int) -> TypeIs[CellDigit]:
    return 0 <= value <= CELL_DIGIT_MINE
