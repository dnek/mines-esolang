# Mines [![PyPI](https://img.shields.io/pypi/v/mines-esolang)](https://pypi.org/project/mines-esolang/)

<img src="assets/mines_256.png" height="64px" alt="Mines logo">

A Minesweeper-driven [esolang](https://en.wikipedia.org/wiki/Esoteric_programming_language).

- 日本語版はこちら [README_ja.md](README_ja.md)

## Overview

Mines is a programming language that executes commands in response to operations to play Minesweeper.

## Language specifications

### Design philosophy

Mines is designed mainly to meet the following criteria.

- Minesweeper-like
- Easy to implement straightforwardly
- Interesting as an esolang

Note that Mines is designed under the influence of [Piet](https://www.dangermouse.net/esoteric/piet.html), and esolang here is often assumed to be Piet.

In cases where there are multiple competing criteria in designing specifications, the selection is made to satisfy those listed earlier as much as possible.

### Integer division

All integer divisions used in Mines are [**floored division**](https://en.wikipedia.org/wiki/Modulo#Variants_of_the_definition).

In **floored division**, the **quotient** is the largest integer that is not greater than the rational result of dividing the dividend by the divisor.
As a result, if the dividend cannot be divided by the divisor, the **remainder** is the one whose sign is the same as the divisor and whose absolute value is less than the divisor.

Let `//` and `%` be the operators that represent the **quotient** and **remainder** of floored division, respectively.

#### Integer division examples

- `5 // 3 = 1` , `5 % 3 = 2`
- `-4 // 3 = -2` , `-4 % 3 = 2`
- `5 // (-3) = -2` , `5 % (-3) = -1`
- `-4 // (-3) = 1` , `-4 % (-3) = -1`

### Program specifications

Mines **program** has a **board** and a **operation list**.

#### Board

**Board** is a rectangular grid with **number of columns** and **number of rows** both positive.
**Number of columns** of board corresponds to **width**, **number of rows** corresponds to **height**.

A **column index** of a board is an integer starting from `0` and less than the number of columns of the board.
A **row index** of a board is an integer starting from `0` and less than the number of rows of the board.

Board has **coordinates** corresponding to all the different pairs of **column indices** and **row indices**, one for each.
The **coordinate** of board corresponding to column index `i` and row index `j` is denoted as `(i, j)`.

An **unwrapped column index** of board is an integer, which represents the column index whose value is the remainder given by dividing it by the number of columns of the board.
An **unwrapped row index** of board is an integer, which represents the row index whose value is the remainder given by dividing it by the number of row of the board.

Board has **board cells** corresponding to all its coordinates, one for each.
Let `i` denote the **column index** and `j` the **row index** of a board cell corresponding to the coordinate `(i, j)`.

A **board cell** is either a **safe cell** or a **mine cell**.

When the absolute difference of the row indices and column indices of two distinct board cells is less than or equal to `1` each, those board cells are **adjacent** to each other.

A board cell has a **digit**.
The **digit** of a safe cell is the number of mine cells adjacent to it.
The **digit** of a mine cell is `9`.

#### Operation list

**Operation list** is a [singly circular linked list](https://en.wikipedia.org/wiki/Linked_list#Circular_linked_list) with one or more **operations** as elements.

An **operation** is either a **click operation** or a **switch operation** or a **restart operation** or a **no operation**.

A **click operation** has a **coordinate** and a **mouse button**.

The **coordinate** of a click operation is a coordinate of board.
The board cell corresponding to the coordinate of a click operation is called the **operation target cell**.

A mouse button is either **left button** or **right button**.

### Syntax rules

Mines source code is a single Unicode string.

Hereinafter, a newline refers to `\n`.

Half-width spaces, `\t`, `\v`, `\f`, and `\r` characters that appear in source code are ignored.

For each line of source code, if there is any `#`, each character from there to the end of the line (not including newline) is ignored.

Source code consists of zero or more **header lines** and one **program**, separated by newlines in this order.

A **header line** is represented by an empty string.

**Program** is represented by the **board** and **operation list** separated by a newline in this order.

**Board** is represented by all **rows** separated by newlines in the row index order.

The **row** of row index `i` of board is represented by joining all the **board cells** of row index `i` in the column index order.

A **safe cell** is represented by `.`.

A **mine cell** is represented by `*`.

**Operation list** is represented by all **operations** separated by newlines in order.

A **click operation** is represented by connecting the **unwrapped column index** representing `i`, the **mouse button**, and the **unwrapped row index** representing `j` in this order, with `(i, j)` as its coordinate.

**Unwrapped column index** and **unwrapped row index** are each expressed in decimal notation so that they match the regular expression `/^[+-]?[0-9]+$/`.

**Left button** is represented by `,`.

**Right button** is represented by `;`.

A **switch operation** is represented by `!`.

A **restart operation** is represented by `@`.

A **no operation** is represented by an empty string.

Below is an example of source code consisting of 2 header lines and a program with a board of 4 columns and 3 rows and 6 operations, and the contents of each operation.

```
# You can write header comments.

.*.* # Board is rectangular.
...*
.**.
0,0
-1, -1 # Spaces are ignored.

10;-10
!
@
```

| Operation | Content                                                                                          |
| --------- | ------------------------------------------------------------------------------------------------ |
| `0,0`     | Click operation with coordinate `(0, 0)` (top left) and left button                              |
| `-1,-1`   | Click operation with coordinate `(-1 % 4, -1 % 3)`, i.e. `(3, 2)` (bottom right) and left button |
|           | No operation                                                                                     |
| `9;-10`   | Click operation with coordinate `(9 % 4, -10 % 3)`, i.e. `(1, 2)` and right button               |
| `!`       | Switch operation                                                                                 |
| `@`       | Restart operation                                                                                |

### Program execution rules

#### Runtime state

The interpreter has the following states during program execution.

- A **player**
- An **operation pointer**
- An **operation queue**
- A **stack**
- An **input buffer**

The **player** has the following states.

- A **game status**
- **cell states** corresponding to each of the board cells
- A **flag mode**

The **game status** takes the value of either **playing** or **cleared** or **over**.
The initial value of game status is **playing**.

A **cell state** takes the value of either **unopened** or **flagged** or **opened**.
The initial value of a cell state is **unopened**.

When a cell state `A` corresponds to a board cell `B`, `A` is called the **state** of `B`.

When a state of board cell with the digit `0` changes from **unopened** to **opened**, each of its adjacent board cells with the status **unopened** immediately becomes **opened**.

When all safe cells are each **opened**, the game status immediately becomes **cleared**.

The **flag mode** takes the value of either **on** or **off**.
The initial value of flag mode is **off**.

The **operation pointer** points to a single operation in the operation list.
The operation pointer initially points to the first operation in the operation list.

Operation pointer **advances** means that the operation pointed to by the operation pointer moves to the linked destination in the circular linked list.

When the operation pointer is **requested** for an operation, it returns the operation it is pointing to and then advances once.

The **operation queue** is a queue that contains zero or more operations.
The operation queue is initially empty.

The **stack** is a stack that contains zero or more integers.
The stack is initially empty.

To **reverse** the stack is the process defined below.

- Pop values from the stack until the stack is empty, then push them in the order they were popped.

To **roll** the stack with depth `d` and number of rolls `r` is the process defined below.

- If `|d| < 2` or `r = 0`, do nothing.
- If `d > 1` and `r = 1`, pop `d` times from the stack, push the first popped value, and push the remaining popped values in the reverse order of the pop order.
- If `d > 1` and `r != 1`, repeat rolling the stack `r % d` times with depth `d` and number of rolls `1`.
- If `d < -1`, reverse the stack, roll the stack with depth `-d` and number of rolls `r`, and reverse the stack again.

The **input buffer** is a Unicode string.
The initial value of input buffer is an empty string.

When a reference after the tail of the input buffer is attempted, it receives input from the standard input as appropriate, adds it to the tail, and then continues to be referenced.
However, once the standard input indicates `EOF`, it receives no input.

When the input buffer is requested for an **integer**, it removes from the beginning the string matching the regular expression `/^\s*[+-]?[0-9]+$/`, parses it into an integer, and returns it.

When the input buffer is requested for a **Unicode code point**, it removes from the beginning the string equivalent to one unit in Unicode code points, converts it to a Unicode code point, and returns it.

#### Operation instructions

Each time the player is instructed to do an **operation**, it performs it as follows.

When the flag mode is **off**, a **click operation** is performed as a **left click operation** if the mouse button is the left button, and as a **right click operation** if the mouse button is the right button.
When the flag mode is **on**, the opposite is true.

For a **left click operation**, if the state of the operation target cell is **unopened**, then perform the following.

- If the digit of the operation target cell is `9`, set the game status to **over**.
- Otherwise, set its cell state to **opened**.

For a **right click operation**, perform the following depending on the state of the operation target cell.

- If **unopened**, set it to **flagged**.
- If **flagged**, set it to **unopened**.
- If **opened**, let `F` be the set of board cells adjacent to the operation target cell and whose states are **flagged** and `U` be the set of those that are **unopened**, and perform the following.

    - If the number of elements in `F` matches the digit of the operation target cell and the number of elements in `U` is positive, then perform **Chord**.
    - **Chord** does the following.
        - If `U` contains any board cells with the digit `9`, set the game status to **over**.
        - Otherwise, set each state of `U` to **opened**.

For a **switch operation**, if the flag mode is **on**, set it to **off**; if it is **off**, set it to **on**.

For a **restart operation**,set all cell states to **unopened** and the game status to **playing**.

For a **no operation**, do nothing.

#### Commands

Each time the player performs an operation, the interpreter selects one type of **command**.

If a command pops a fixed number of times from the stack at the beginning of its execution flow, the series of pops is called the **constant times pop**.

If a situation arises during command execution that prevents the execution flow from proceeding correctly, a **command error** occurs.

##### Command list

There are 25 commands in total.

The following table summarizes the names and execution flows of each command.

Here, apply the following to each explanation.
- Assume that the command was selected when the player executed operation `A`.
- Let `B` be the set of board cells whose states changed from **unopened** to **opened** during the execution of `A`.
- If the command pops `n` times from the stack by the constant times pop, describe `n` in the **Number of pops** column. Also, let the element taken out by the `i`th pop be `p(i)`. Here, `i` is an integer starting from `0` and ending with `n - 1`.

| Name          | Number of pops | Execution flow (excluding constant times pop)                                                  |
| ------------- | -------------- | ---------------------------------------------------------------------------------------------- |
| `push(n)`     | -              | Push the digit of the operation target cell of `A` onto the stack.                             |
| `push(count)` | -              | Push the number of elements in `B` onto the stack.                                             |
| `push(sum)`   | -              | Push the sum of each digit of `B` onto the stack.                                              |
| `pop`         | `1`            | Do nothing.                                                                                    |
| `positive`    | `1`            | Push `1` onto the stack if `p(0) > 0`, otherwise push `0` onto the stack.                      |
| `dup`         | `1`            | Push `p(0)` onto the stack twice.                                                              |
| `add`         | `2`            | Push `p(1) + p(0)` onto the stack.                                                             |
| `sub`         | `2`            | Push `p(1) - p(0)` onto the stack.                                                             |
| `mul`         | `2`            | Push `p(1) * p(0)` onto the stack.                                                             |
| `div`         | `2`            | Push `p(1) // p(0)` onto the stack.                                                            |
| `mod`         | `2`            | Push `p(1) % p(0)` onto the stack.                                                             |
| `not`         | `1`            | Push `1` onto the stack if `p(0) = 0`, otherwise push `0` onto the stack.                      |
| `roll`        | `2`            | Roll the stack with depth `p(1)` and number of rolls `p(0)`.                                   |
| `in(n)`       | -              | Request an integer from the input buffer and push it onto the stack.                           |
| `in(c)`       | -              | Request a Unicode code point from the input buffer and push it onto the stack.                 |
| `out(n)`      | `1`            | Output `p(0)` to standard output in decimal notation.                                          |
| `out(c)`      | `1`            | Output the character whose Unicode code point is `p(0)` to standard output.                    |
| `skip`        | `1`            | Advance the operation pointer `p(0) % l` times, where `l` is the length of the operation list. |
| `perform(l)`  | `2`            | Enqueue the operation obtained by parsing `p(1),p(0)` into the operation queue.                |
| `perform(r)`  | `2`            | Enqueue the operation obtained by parsing `p(1);p(0)` into the operation queue.                |
| `reset(l)`    | -              | Enqueue a restart operation into the operation queue.                                          |
| `reset(r)`    | -              | Pop from the stack until it is empty, and enqueue a restart operation to the operation queue.  |
| `swap`        | `2`            | Push `p(0)` and `p(1)` onto the stack in this order.                                           |
| `reverse`     | -              | Reverse the stack.                                                                             |
| `noop`        | -              | Do nothing.                                                                                    |

##### Command error list

There are 4 command errors in total.

The following table summarizes the names of each command error, their occurrence conditions, and the commands that can cause them.

| Name                  | Occurrence condition                                               | Commands                                                       |
| --------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------- |
| `StackUnderflowError` | Attempt to pop from the empty stack.                               | All commands that do a constant times pop or roll on the stack |
| `ZeroDivisionError`   | Attempt division with `0` as the divisor.                          | `div`, `mod`                                                   |
| `InputMismatchError`  | The input buffer cannot return the requested value.                | `in(n)`, `in(c)`                                               |
| `UnicodeRangeError`   | Attempt to obtain a character outside the Unicode code point range | `out(c)`                                                       |

##### Command selection flow

The command is selected in the following selection flow by performing operation `A`.
Here, let the state of the operation target cell of `A` immediately before the execution of `A` be `B`, and the digit be `C`.

- `A` is a left click operation
    - `B` was **unopened**
        - `C = 0` -> `push(count)`
        - `0 < C < 9` -> `push(n)`
        - `C = 9` -> `reset(l)`
    - `B` was **flagged** -> `noop`
    - `B` was **opened**
        - `C = 0` -> `pop`
        - `C = 1` -> `positive`
        - `C = 2` -> `dup`
        - `C = 3` -> `add`
        - `C = 4` -> `sub`
        - `C = 5` -> `mul`
        - `C = 6` -> `div`
        - `C = 7` -> `mod`
        - `C = 8` -> `perform(l)`
- `A` is a right click operation -> `swap`
    - `B` was **unopened** -> `swap`
    - `B` was **flagged** -> `swap`
    - `B` was **opened**
        - Chord was performed
            - Game status has become **over** -> `reset(r)`
            - Otherwise -> `push(sum)`
        - Chord was not performed
            - `C = 0` -> `push(n)`
            - `C = 1` -> `not`
            - `C = 2` -> `roll`
            - `C = 3` -> `in(n)`
            - `C = 4` -> `in(c)`
            - `C = 5` -> `out(n)`
            - `C = 6` -> `out(c)`
            - `C = 7` -> `skip`
            - `C = 8` -> `perform(r)`
- `A` is a switch operation -> `reverse`
- `A` is a restart operation -> `noop`
- `A` is a no operation -> `noop`

#### Program execution flow

The interpreter executes the program by following the steps below from 1.

1. If the game status is **cleared**, terminate program execution.
2. If the operation queue is empty, request an operation from the operation pointer and enqueue it.
3. Dequeue from the operation queue and instruct the player to perform the taken operation.
4. Select a command based on the operation performed by the player.
5. Verify whether a command error occurs when the selected command is executed.
6. If the verification result shows that no command error occurs, execute the command.
7. Return to step 1.

## Processor implementation

If a runtime error occurs before the processor starts executing the program flow, the process should be terminated abnormally.
In particular, if the source code does not comply with the syntax rules, a syntax error should occur before the program is executed, and the process should be terminated abnormally.

Once the program execution flow has started, the process should not be terminated due to behavior that violates the language specification, except in unavoidable cases such as external interrupts.

For example, the size of the stack and the range of values that integers can take are ideally infinite, but it is difficult for the processor to reproduce them perfectly.
When the processor actually loses its ability to reproduce them (typically when errors such as stack overflow or arithmetic overflow occur), it is desirable to transition to a process such as performing no operation infinitely.

Note that the following behaviors do not violate the language specifications.

- Obtaining verification results indicating that a command error will occur
- Game status becomes **over**

## Source code examples

- [examples/](examples)

## Execution environment

### Install

- [uv](https://docs.astral.sh/uv/) (recommended)

```sh
uv tool install mines-esolang
```

- [pipx](https://pipx.pypa.io/stable/)

```sh
pipx install mines-esolang
```

- From the source

```sh
git clone https://github.com/dnek/mines-esolang
cd mines-esolang
uv tool install -e .
```

### Uninstall

```sh
uv tool uninstall mines-esolang
```

```sh
pipx uninstall mines-esolang
```

### Usage

Check the version with `-V`.

```sh
mines -V
```

Show help with `-h`.

```sh
mines -h
```

Execute a program by specifying the file path of the source code.

```sh
mines examples/hello.mines
```

To replace standard input with file input, specify the file path with `-i`.

```sh
mines examples/cat.mines -i examples/cat.mines
```

To replace standard input directly with a string, specify the string with `-e`.

```sh
mines examples/add.mines -e "1 2"
```

You can use redirection or pipes as appropriate.

```sh
echo -n "🐱meow" | mines examples/cat.mines
```

If you do not use `-i`, `-e`, redirection, or pipes, interactive input will be accepted as appropriate.

Enable debug mode with `-d`.
You can step through the execution while checking the state at runtime.

```sh
mines examples/hello.mines -d
```

However, debug mode cannot be executed if standard input is not connected to the terminal due to redirection or piping.

### Bonus

Installing `mines-esolang` also adds the command `mines-game`, which allows you to play a normal Minesweeper game.

Play by specifying the level with `-l`.
Levels can be specified as `beginner`, `intermediate`, `expert`, or their initials.

```sh
mines-game -l b
```

Play by specifying the width, height, and number of mines on the board with `-c`.

```sh
mines-game -c 48 24 256
```

By specifying the file path of the source code, you can play the board of that program.

```sh
mines-game examples/hello.mines
```

Except when playing a board from program, mines are placed so that the digit of the first cell opened is `0`.

## Author

- [**DNEK**](https://github.com/dnek)

## Related projects

- [Mines Web Interpreter](https://mug.sh/mines-editor/) by [sh-mug](https://github.com/sh-mug)

    A web application that serves as a code editor and interpreter for Mines.

- [Pietron](https://github.com/dnek/pietron) by DNEK

    An IDE for the esolang Piet.

- [UnambiSweeper](https://dnek.net/en/unambi) by DNEK

    A Minesweeper app that can be solved logically to the end.
    Available for Android and iOS.

## License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
