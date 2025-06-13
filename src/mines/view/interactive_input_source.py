import os
from collections import deque
from collections.abc import Iterator
from sys import stderr
from typing import TextIO

from mines.runtime.input_buffer import InputSource
from mines.view.ansi import Ansi


class InteractiveInputSource(InputSource):
    __stdin_buffer: deque[str]
    __is_eof_comfirmed: bool
    __input_io: TextIO

    def __init__(self, input_io: TextIO) -> None:
        self.__stdin_buffer = deque()
        self.__is_eof_comfirmed = False
        self.__input_io = input_io

    def __del__(self) -> None:
        self.__input_io.close()

    def __write_and_flush_stderr(self, message: str) -> None:
        stderr.write(message)
        stderr.flush()

    def __fill_buffer(self) -> str:
        if self.__input_io.isatty():
            eof_key_str = "^Z" if os.name == "nt" else "^D"
            prompt_str = f"add input or EOF({eof_key_str}) >>> "
            self.__write_and_flush_stderr(str(Ansi(prompt_str, fg=5, bold=True)))

        line = self.__input_io.readline()

        if len(line) > 0:
            self.__stdin_buffer.extend(c for c in line)
        elif self.__input_io.isatty():
            self.__write_and_flush_stderr(f"{Ansi('EOF', fg=2, bold=True)}\n")

        return line

    def __iter__(self) -> Iterator[str]:
        yield from self.__stdin_buffer

        if self.__is_eof_comfirmed:
            return

        line = self.__fill_buffer()
        yield from line

        self.__is_eof_comfirmed = True

    def dequeue(self) -> str:
        return self.__stdin_buffer.popleft()

    def get_buffered_len(self) -> int:
        return len(self.__stdin_buffer)

    def get_is_eof_confirmed(self) -> bool:
        return self.__is_eof_comfirmed
