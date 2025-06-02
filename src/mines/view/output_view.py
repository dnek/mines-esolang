from io import SEEK_END, StringIO

from mines.view.ansi import Ansi, uncntrl


class OutputView:
    __max_len: int = 320
    __max_lf: int = 4
    __output_io: StringIO

    def __init__(self, output_io: StringIO) -> None:
        self.__output_io = output_io

    def get_str(self) -> str:
        origin_pos = self.__output_io.tell()

        self.__output_io.seek(0, SEEK_END)
        buffered_len = self.__output_io.tell()
        lf_count = 0
        end_pos = buffered_len

        while end_pos > 0:
            self.__output_io.seek(end_pos - 1)
            c = self.__output_io.read(1)
            if c == "\n":
                lf_count += 1
            if end_pos + self.__max_len == buffered_len or lf_count == self.__max_lf:
                break
            end_pos -= 1

        output_chars: list[str] = []
        if end_pos > 0:
            output_chars.append(str(Ansi(f"({end_pos} chars and)", fg=0, bg=7)))
            output_chars.append(uncntrl("\n"))
        self.__output_io.seek(end_pos)
        output_chars.extend(uncntrl(c) for c in self.__output_io.read())

        self.__output_io.seek(origin_pos)

        return "".join(output_chars)
