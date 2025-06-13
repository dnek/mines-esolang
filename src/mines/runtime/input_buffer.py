import re
from abc import ABC, abstractmethod
from collections.abc import Iterator


class InputSource(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[str]:
        pass

    @abstractmethod
    def dequeue(self) -> str:
        pass

    @abstractmethod
    def get_buffered_len(self) -> int:
        pass

    @abstractmethod
    def get_is_eof_confirmed(self) -> bool:
        pass


class InputBufferInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in input buffer: {message}")


class InputBuffer:
    __input_queue: InputSource

    def __init__(self, input_source: InputSource) -> None:
        self.__input_queue = input_source

    def __parse_next_integer(self, *, consume_buffer: bool) -> int | None:
        space_count = 0
        matched_str = ""

        for c in self.__input_queue:
            if len(matched_str) == 0:
                if c.isspace():
                    space_count += 1
                    continue

                if re.compile(r"^[0-9+-]$").match(c):
                    matched_str += c
                    continue

                return None

            if re.compile(r"^[0-9]$").match(c):
                matched_str += c
            else:
                break

        if matched_str in ["", "+", "-"]:
            return None

        if consume_buffer:
            for _ in range(space_count + len(matched_str)):
                self.__input_queue.dequeue()

        return int(matched_str)

    def validate_request_integer(self) -> bool:
        return self.__parse_next_integer(consume_buffer=False) is not None

    def request_integer(self) -> int:
        next_integer = self.__parse_next_integer(consume_buffer=True)

        if next_integer is None:
            message = "Input does not match an integer."
            raise InputBufferInternalError(message)

        return next_integer

    def validate_request_char(self) -> bool:
        for _ in self.__input_queue:
            return True
        return False

    def request_char(self) -> int:
        return ord(self.__input_queue.dequeue())
