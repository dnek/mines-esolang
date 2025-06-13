from argparse import ArgumentParser
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from sys import stderr, stdin, stdout
from typing import TextIO

from mines.__version__ import __version__
from mines.presenter.debugger import Debugger
from mines.program.parser import parse
from mines.runtime.runner import Runner
from mines.view.interactive_input_source import InteractiveInputSource


@dataclass
class Args:
    source: str = ""
    input: str | None = None
    echo: str | None = None
    debug: bool | None = None


def __get_input_io(args: Args) -> TextIO:
    if args.input is not None:
        return Path(args.input).open(encoding="utf-8")

    if args.echo is not None:
        return StringIO(args.echo)

    return stdin


def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-V", "--version", action="version", version=__version__)
    arg_parser.add_argument("source", type=str, help="source file path")
    arg_parser.add_argument("-i", "--input", type=str, help="file path to input")
    arg_parser.add_argument("-e", "--echo", type=str, help="string to input")
    arg_parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug mode",
    )
    args = arg_parser.parse_args(namespace=Args())

    is_debug_mode = bool(args.debug)
    if is_debug_mode and not stdin.isatty():
        message = "Debug mode is unavailable since stdin is not connected to tty.\n"
        stderr.write(message)
        return

    with Path(args.source).open(encoding="utf-8") as f:
        code = f.read()
    program = parse(code)
    with __get_input_io(args) as input_io:
        input_source = InteractiveInputSource(input_io)
        if is_debug_mode:
            debugger = Debugger(program, input_source)
            debugger.run()
        else:
            runner = Runner(program, input_source, stdout, None)
            runner.run()
