from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path
from sys import stderr, stdin
from typing import Literal, NamedTuple

from mines.__version__ import __version__
from mines.player.board import BoardSize
from mines.presenter.game import Game
from mines.program.parser import parse

LevelName = Literal["beginner", "intermediate", "expert"]
LEVEL_NAMES: tuple[LevelName, ...] = ("beginner", "intermediate", "expert")
INITIAL_TO_LEVELS: dict[str, LevelName] = {level[0]: level for level in LEVEL_NAMES}
LEVEL_CHOICES = (*LEVEL_NAMES, *INITIAL_TO_LEVELS.keys())


class GameCliInternalError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Internal error in game cli: {message}")


class LevelConfig(NamedTuple):
    width: int
    height: int
    mine_number: int


class CustomLevelConfigError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid custom level config error: {message}")


@dataclass
class Args:
    source: str | None = None
    level: str | None = None
    custom: list[int] | None = None


def __validate_level_config(level_config: LevelConfig) -> None:
    width, height, mine_number = level_config

    if width < 1:
        message = "Width must be positive."
        raise CustomLevelConfigError(message)

    if height < 1:
        message = "Height must be positive."
        raise CustomLevelConfigError(message)

    if mine_number < 0:
        message = "Mine number must not be negative."
        raise CustomLevelConfigError(message)

    max_exclusion_count = min(3, width) * min(3, height)
    if width * height - mine_number < max_exclusion_count:
        message = "Mine number is too large relative to the width and height."
        raise CustomLevelConfigError(message)


def main() -> None:
    arg_parser = ArgumentParser()
    arg_parser.add_argument("-V", "--version", action="version", version=__version__)
    arg_parser.add_argument("source", nargs="?", type=str, help="source file path")
    arg_parser.add_argument(
        "-l",
        "--level",
        type=str,
        choices=LEVEL_CHOICES,
        help="game level",
    )
    arg_parser.add_argument(
        "-c",
        "--custom",
        nargs=3,
        type=int,
        help="custom (width, height, mine number) for game level",
    )
    args = arg_parser.parse_args(namespace=Args())

    if not stdin.isatty():
        message = "Mines game is unavailable since stdin is not connected to tty.\n"
        stderr.write(message)
        return

    if args.source:
        path = Path(args.source)
        with path.open(encoding="utf-8") as f:
            code = f.read()
        cell_digits = parse(code).cell_digits
        game = Game(path.name, cell_digits.get_board_size(), cell_digits)
    else:
        if args.level:
            if args.level in LEVEL_NAMES:
                level_name = args.level
            else:
                level_name = INITIAL_TO_LEVELS.get(args.level)
                if level_name is None:
                    message = "level name is invalid."
                    raise GameCliInternalError(message)

            match level_name:
                case "beginner":
                    level_config = LevelConfig(width=9, height=9, mine_number=10)
                case "intermediate":
                    level_config = LevelConfig(width=16, height=16, mine_number=40)
                case "expert":
                    level_config = LevelConfig(width=30, height=16, mine_number=99)
        elif args.custom:
            level_name = "custom"
            level_config = LevelConfig(*args.custom)
            __validate_level_config(level_config)
        else:
            arg_parser.print_help()
            return

        game = Game(
            level_name,
            BoardSize(width=level_config.width, height=level_config.height),
            level_config.mine_number,
        )

    game.run()
