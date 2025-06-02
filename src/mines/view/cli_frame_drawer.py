from sys import stderr

from mines.view.ansi import ANSI_END_FRAME, ANSI_INIT, ANSI_LF, ANSI_START_FRAME, Ansi


class CliFrameDrawer:
    __lines: list[str]

    def __init__(self) -> None:
        self.__lines = []

        stderr.write(ANSI_INIT)

    def add_line(self, line: str, title: str | None = None) -> None:
        self.__lines.append(
            f"{Ansi(f'[{title}]', bold=True, faint=True)} {line}" if title else line,
        )

    def draw_frame(self) -> None:
        stderr.write(ANSI_START_FRAME)
        stderr.write(ANSI_LF.join(self.__lines))
        stderr.write(ANSI_END_FRAME)
        stderr.flush()
