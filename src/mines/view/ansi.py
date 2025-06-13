import os
from dataclasses import dataclass

# enable ANSI escape code on Windows
if os.name == "nt":
    from ctypes import windll

    kernel32 = windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

ANSI_INIT = "\x1b[H\x1b[J"
ANSI_START_FRAME = "\x1b[?25l\x1b[H"
ANSI_END_FRAME = "\x1b[J\x1b[?25h"
ANSI_LF = "\x1b[K\n"

_SGR_BOLD = 1
_SGR_FAINT = 2
_SGR_FG_COLOR_OFFSET = 30
_SGR_BG_COLOR_OFFSET = 40
_SGR_DEFAULT_COLOR_OFFSET = 9


@dataclass
class Ansi:
    raw: str
    fg: int = _SGR_DEFAULT_COLOR_OFFSET
    bold: bool = False
    faint: bool = False
    bg: int = _SGR_DEFAULT_COLOR_OFFSET

    def __repr__(self) -> str:
        params: list[int] = []
        if self.bold:
            params.append(_SGR_BOLD)
        if self.faint:
            params.append(_SGR_FAINT)
        if self.fg != _SGR_DEFAULT_COLOR_OFFSET:
            params.append(_SGR_FG_COLOR_OFFSET + self.fg)
        if self.bg != _SGR_DEFAULT_COLOR_OFFSET:
            params.append(_SGR_BG_COLOR_OFFSET + self.bg)

        if len(params) == 0:
            return self.raw

        params_str = ";".join(str(param) for param in params)
        return f"\x1b[{params_str}m{self.raw}\x1b[m"


def em(value: str) -> str:
    return str(Ansi(value, bold=True))


ORD_SP = 32
ORD_DEL = 127


def uncntrl(c: str) -> str:
    code_point = ord(c)
    if code_point < ORD_SP or code_point == ORD_DEL:
        match c:
            case "\t":
                return c
            case "\n":
                return ANSI_LF
            case _:
                return str(Ansi(f"^{chr(code_point + 64 & 127)}", fg=0, bg=7))
    return c
