import os

if os.name == "nt":
    import msvcrt

    def get_key() -> str:
        first = msvcrt.getch()
        match first:
            case b"\x00" | b"\xe0":
                second = msvcrt.getch()
                return {
                    b"H": "UP",
                    b"P": "DOWN",
                    b"M": "RIGHT",
                    b"K": "LEFT",
                }.get(second, f"UNKNOWN({second})")
            case b"\r":
                return "\n"
            case _:
                return first.decode(errors="ignore")
else:
    from sys import stdin
    from termios import TCSADRAIN, tcgetattr, tcsetattr
    from tty import setcbreak

    def get_key() -> str:
        fd = stdin.fileno()
        old = tcgetattr(fd)
        try:
            setcbreak(fd)
            first = stdin.read(1)
            match first:
                case "\x1b":
                    second = stdin.read(1)
                    third = stdin.read(1)
                    seq = second + third
                    return {
                        "[A": "UP",
                        "[B": "DOWN",
                        "[C": "RIGHT",
                        "[D": "LEFT",
                    }.get(seq, f"UNKNOWN(\\x1b{seq})")
                case "\r":
                    return "\n"
                case _:
                    return first
        finally:
            tcsetattr(fd, TCSADRAIN, old)
