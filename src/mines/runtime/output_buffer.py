from typing import TextIO

MAX_UNICODE_CODEPOINT = 0x10FFFF


class OutputBuffer:
    __output_io: TextIO

    def __init__(self, output_io: TextIO) -> None:
        self.__output_io = output_io

    def write_as_integer(self, value: int) -> None:
        self.__output_io.write(str(value))

    def validate_write_as_char(self, value: int) -> bool:
        return 0 <= value <= MAX_UNICODE_CODEPOINT

    def write_as_char(self, value: int) -> None:
        self.__output_io.write(chr(value))
