from collections.abc import Callable
from sys import stderr

from mines.view.ansi import Ansi
from mines.view.getch import get_key


class Prompt:
    __descs: list[str]
    __actions: dict[str, Callable[[], None]]

    def __init__(self) -> None:
        self.__descs = []
        self.__actions = {}

    def add_desc(self, desc: str) -> None:
        self.__descs.append(desc)

    def add(
        self,
        keys: str | tuple[str, ...],
        action: Callable[[], None],
        desc: str | None,
    ) -> None:
        if isinstance(keys, str):
            keys = (keys,)
        for key in keys:
            self.__actions[key] = action

        if desc:
            self.add_desc(desc)

    def show(self) -> None:
        prompt_str = "  ".join(self.__descs)
        stderr.write(str(Ansi(prompt_str, fg=6)))
        stderr.flush()

        while True:
            key = get_key()
            action = self.__actions.get(key)

            if not action:
                continue

            action()
            break
