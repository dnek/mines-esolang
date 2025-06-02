from mines.runtime.input_buffer import InputSource
from mines.view.ansi import Ansi, uncntrl


class InputView:
    __max_len: int = 320
    __max_lf: int = 4
    __input_source: InputSource

    def __init__(self, input_source: InputSource) -> None:
        self.__input_source = input_source

    def get_str(self) -> str:
        buffered_len = self.__input_source.get_buffered_len()
        input_iter = iter(self.__input_source)
        lf_count = 0
        input_chars: list[str] = []

        for i in range(buffered_len):
            c = next(input_iter)
            if c == "\n":
                lf_count += 1
            if i == self.__max_len or lf_count == self.__max_lf:
                input_chars.append(uncntrl("\n"))
                and_chars_str = f"(and {buffered_len - i} chars)"
                input_chars.append(str(Ansi(and_chars_str, fg=0, bg=7)))
                break
            input_chars.append(uncntrl(c))

        confirmed_str = "EOF" if self.__input_source.get_is_eof_confirmed() else "..."
        input_chars.append(str(Ansi(confirmed_str, fg=0, bg=7)))

        return "".join(input_chars)
