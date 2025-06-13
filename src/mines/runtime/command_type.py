from typing import Literal

CommandType = Literal[
    "push(n)",
    "push(count)",
    "push(sum)",
    "pop",
    "positive",
    "dup",
    "add",
    "sub",
    "mul",
    "div",
    "mod",
    "not",
    "roll",
    "in(n)",
    "in(c)",
    "out(n)",
    "out(c)",
    "skip",
    "perform(l)",
    "perform(r)",
    "reset(l)",
    "reset(r)",
    "swap",
    "reverse",
    "noop",
]


CommandErrorType = Literal[
    "StackUnderflowError",
    "ZeroDivisionError",
    "InputMismatchError",
    "UnicodeRangeError",
]
