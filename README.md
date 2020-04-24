# Mines [![PyPI](https://img.shields.io/pypi/v/mines-esolang)](https://pypi.org/project/mines-esolang/)

An esoteric language inspired by Minesweeper.

- 日本語はこちら（[README_ja.md](README_ja.md)）。

## Overview

Mines is a programming language in which programs are executed by operations that mimic the gameplay of Minesweeper.

## Program description

A Mines program consists of a field and an operation list in this order with a line break.

**Field** is represented by a rectangular grid consisting of `.` and `*`.
Where `.` is a safe cell, and `*` is a mine cell.

**Operation list** consists of one or more operations separated by `\n`.

**An operation** is represented by two integers separated by `,` or `;`, or `!`, or a blank line.
Blank lines immediately after the field and at the end of the file are also counted as operations.

**Two integers** indicate the column and row numbers from the top left of the field, and the delimiter indicates the mouse button to click.
Where `,` is a left click and `;` is a right click.

**Column and row numbers** may be negative or point outside the range of the field.
These are converted into non-negative remainders divided by the width or height of the field, respectively.

**`!`** indicates the flagging mode switch (see below).

Half-width whitespaces and characters in `\t\r\f\v` appearing in the program are ignored.
Also, strings from # to the end of the line are ignored.
This means that the program can contain **comments**.

The following is an example of a program with a 4x3 field and 5 operations, and the meaning of each operation.

```
.*.* #This is a comment.
...*
.**.
0,0
-1, -1 #Spaces are ignored.

10;-10
!
```

| Operation | Meaning |
----|----
| `0,0` | Left click on the top left cell. |
| `-1,-1` | Right click on the bottom right cell (equal to `3,2` ). |
|  | do nothing. |
| `9;-10` | Right-click on the (9 % 4)th cell from the left and the (-10 % 3)th cell from the top (equal to `1;2` ). |
| `!` | Switch the flagging mode. |

## Program processing

The Mines interpreter has a **operation pointer** (OP), which by default points to the top of the operation list.
The interpreter performs an operation pointed by OP on the field and then advances the OP by one.
After the bottom operation is performed, the OP returns to the top operation and continues operations.

For each operation, **an command** is selected and executed according to the result and the state of the cell in which the operation was performed.

If **game over** is occurred by an operation, the program does not terminate and the field returns to its initial state (no revealed cells and no flags) and the game resumes (the OP is not initialized).

The interpreter has **a stack** of signed integers for storage, which is manipulated by the commands.
The initial state of the stack is empty, and it can have an infinite number of values as long as the processing system allows.

In addition, the interpreter manages **the flagging mode**, which is initially off.
It is toggled between on and off by an operation of the flagging mode switch.
Game over does not initialize the flag mode.

After each command is executed, if "each safe cell" or "each mine cell" is opened one or more times throughout the entire gameplay, the program **terminates** (this behavior is different from game clear on a regular minesweeper).

## Performance of operations

**Left click** behaves just like it does in most minesweeper apps.

Left click on an unopened cell will open it.
If you open a mine, it's game over.

Left click on a revealed cell has no effect on the field, but some command may be executed.

**Right click** also behaves like it does in many minesweeper apps.

Right click on an unopened cell will put up a flag or remove it.

Right click on a revealed cell will open all adjacent unopened cells if the number on the cell is equal to the number of flags standing around it.
If trying to open some mines, it's game over.
This operation is called "Chord" and in some apps, Chord is bound to a long press or other mouse button.

If a cell opened by either click is empty, the surrounding cells are also opened recursively (the flags standing in the cell being opened are removed and opened).

**Flagging mode switch** is a feature that most mobile minesweeper apps have, and it behaves just as well.
When the flagging mode is on, the left-click and right-click are treated swapped.
For example, left click on an unopened cell will put up a flag or remove it, and the command corresponding to it will be executed.

Nothing happens with an operation of **blank line** (the OP proceeds as usual).

## Commands

The cell number "0" represents a blank cell and the number "9" represents a mine cell.

"Push", "pop", etc. all refer to operations on the stack.

The first popped value in a command is "p0" and the next popped value is "p1".

### Command errors

When a command cannot be executed correctly because there are not enough values for pops in the stack or 0 division is attempted or so on, this is called **a command error**.
If a command error is likely to occur during the execution, it is treated as if there was no command and the OP proceeds to the next.
Note that game over is not a command error.

The conditions for the occurrence of a command error except for insufficient number of pops are shown in the following tables.

### Flagging mode switch

| Command name | Pop count | Description | error condition |
----|----|----|----
| reverse | 0 | Reverse order of the elements in the entire stack. | - |

### Left click on an unopened cell

#### Flag is standing on the cell

| Command name | Pop count | Cell number | Description | error condition |
----|----|----|----|----
| noop | 0 | Any (because not revealed) | Do nothing | - |

#### Flag is not standing on the cell

| Command name | Pop count | Cell number | Description | error condition |
----|----|----|----|----
| push(count) | 0 | 0 | Push the number of cells opened by this click (≧1) | - |
| push(n) | 0 | 1〜8 | Push the number written in the cell | - |
| reset(l) | 0 | 9 | Reset the field to its initial state and resume the game (stack and OP are not reset, this cell is regarded as opened) | - |

### Right click on an unopened cell

| Command name | Pop count | Cell number | Description | error condition |
----|----|----|----|----
| swap | 2 | Any (because not revealed) | Push p0, then push p1 | - |

### Left click on an revealed cell

| Command name | Pop count | Cell number | Description | error condition |
----|----|----|----|----
| pop | 1 | 0 | Pop | - |
| positive | 1 | 1 | Push 1 if p0 is positive, else push 0 | - |
| dup | 1 | 2 | Push p0 twice | - |
| add | 2 | 3 | Push (p1 + p0) | - |
| sub | 2 | 4 | Push (p1 - p0) | - |
| mul | 2 | 5 | Push (p1 * p0) | - |
| div | 2 | 6 | Push (p1 / p0) | 0 division |
| mod | 2 | 7 | Push (p1 % p0) | 0 division |
| perform(l) | 2 | 8 | Perform an operation of "`p1,p0`" | - |

### Right click on an revealed cell

#### Try to open one or more new cells (Chord)

| Command name | Pop count | Result | Description | error condition |
----|----|----|----|----
| push(sum) | 0 | Success | Push the sum of the numbers written in the cells opened by this click | - |
| reset(r) | Length of stack | Game over | Reset the field and the stack to their initial states and resume the game (OP is not reset, the cells are not regarded as opened) | - |

#### Otherwise
| Command name | Pop count | Cell number | Description | error condition |
----|----|----|----|----
| push(0) | 0 | 0 | Push 0 | - |
| not | 1 | 1 | Push 1 if p0 is 0, else push 0 | - |
| roll | 2 | 2 | Roll the values up to stack depth p1 p0 times (see "Roll Details" for details) | The absolute value of p1 exceeds the length of the stack |
| in(n) | 0 | 3 | Take one integer-parsed value from the beginning of the standard input and push it | Can not parse |
| in(c) | 0 | 4 | Take a single character from the standard input and push its Unicode value | Empty input |
| out(n) | 1 | 5 | Output p0 to the standard output | - |
| out(c) | 1 | 6 | Output a single character whose Unicode value is p0 to the standard output | Invalid Unicode value |
| skip | 1 | 7 | Add p0 to the OP (loop if overflow occurs) | - |
| perform(r) | 2 | 8 | Perform an operation of "`p1;p0`" | - |

##### Roll details

If the stack is `1, 2, 3, 4` with p0 and p1 popped, a single rotation of a value up to a depth of 3 embeds the top value underneath and the stack becomes `1, 4, 2, 3`.

If the number of rotations is negative, for example, if the number of rotations is -1, the opposite manipulatation will be performed and it becomes `1, 3, 4, 2`.

If the depth is negative, e.g. one rotation, the stack is manipulated from the bottom and becomes `2, 3, 1, 4`.

## Examples of implementation

See [examples/](examples) 。

## Install

```
pip3 install mines-esolang
```

Make sure it displays the version.

```
mines -V
```

## How to run the interpreter

Usually do like this.

```
$ mines examples/hello.mines
```

You can also run it directly from the source file.

```
$ python3 mines/mines.py examples/hello.mines
```

Activate the debug mode with `d`.
This outputs a table of numbers in each cell, the time taken to parse the code, and the time taken to run it.

```
$ mines examples/hello.mines -d
```

When the debug mode is active, the command, the stack and the field are output by `c`, `s` and `f` respectively after each operation.
Also, you can perform step executions at the number of operations specified by `l`.

```
$ mines examples/hello.mines -dcsfl 42
```

To get input from a file, specify the file path with `i`.

```
$ mines examples/cat.mines -i README.md
```

To specify a direct input, use `e`.

```
$ mines examples/add.mines -e "1 2"
```

You can use `echo` or `cat` if you want.

```
$ echo -n "meow" | mines examples/cat.mines
```

## Author

- **[DNEK](https://github.com/dnek)**

### Related works

- [Pietron](https://github.com/dnek/pietron) - Cross-platform IDE for Piet (Piet is an esoteric language). The specification of Mines is affected by Piet.

- [UnambiSweeper](https://dnek.app/unambi) - logically solvable Minesweeper app. It supports Android and iOS.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
