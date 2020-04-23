import argparse
from collections import deque
import re
from sys import stdin
from time import perf_counter_ns
from typing import Any, List, Tuple, Union
from mines.__version__ import __version__

def parse_code(filename: str, args: Any) -> Tuple[List[List[int]], int, List[Tuple[int, int, bool]]]:
  debug_mode = args.debug
  if debug_mode:
    parse_start_time = perf_counter_ns()
  raw_code = open(filename, encoding='utf-8').read().split(sep='\n')
  comment_re = re.compile(r'#.*')
  line_re = re.compile(r'\s+', flags=re.ASCII)
  formatted_code = list(map(lambda line: re.sub(line_re, '', re.sub(comment_re, '', line)), raw_code))
  width = len(formatted_code[0])
  if width == 0:
    raise NameError('The first row of field is empty.')
  height = 0

  is_mine = [] #[[bool]]
  field = [] #[[int]]
  mines = 0
  operations: List[Union[Tuple[int, int, bool], bool]] = []

  row_re = re.compile(r'[.*]{{{width}}}'.format(width=width))
  operation_re = re.compile(r'(0|-?[1-9][0-9]*)([,;])(0|-?[1-9][0-9]*)')

  def construct_field():
    nonlocal field
    field = [[-1] * width for _ in range(height)]
    for x in range(height):
      for y in range(width):
        if is_mine[x][y]:
          field[x][y] = 9
          continue
        mine_count = 0
        for i in range(max(0, x - 1), min(height - 1, x + 1) + 1):
          for j in range(max(0, y - 1), min(width - 1, y + 1) + 1):
            if is_mine[i][j]:
              mine_count += 1
        field[x][y] = mine_count

  def parse_operation(line: str) -> Union[Tuple[int, int, bool], bool]:
    if len(line) == 0:
      return False
    elif line == '!':
      return True
    else:
      operation_match = re.fullmatch(operation_re, line)
      if not operation_match:
        raise NameError(f"Command '{line}' is inconsistent.")
      return (int(operation_match[3]) % height, int(operation_match[1]) % width, operation_match[2] == ';') # inverted.

  parsing_field = True
  is_mine_append = is_mine.append
  oeprations_append = operations.append
  for line in formatted_code:
    if parsing_field:
      if not re.fullmatch(row_re, line):
        parsing_field = False
        height = len(is_mine)
        if height == 0:
          raise NameError('No field.')
        construct_field()
        oeprations_append(parse_operation(line))
      else:
        parsed_line = [c == '*' for c in line]
        mines += parsed_line.count(True)
        is_mine_append(parsed_line)
    else:
      oeprations_append(parse_operation(line))
  if len(operations) == 0:
    raise NameError('No operation.')

  if debug_mode:
    parse_end_time = perf_counter_ns()
    print('**field values**')
    print('   ', end='')
    for i in range(len(field[0])):
      print(str(i).rjust(3), end='')
    print()
    for i, l in enumerate(field):
      print(str(i).rjust(3), l)
    print()
    print(f'parse: {(parse_end_time - parse_start_time) / 1000000}ms')
    print()
  return field, mines, operations

def run(field: List[List[int]],
    mines: int,
    operations: List[Union[Tuple[int, int, bool], bool]],
    args: Any):
  debug_mode: bool = args.debug
  if debug_mode:
    output_debug = ''
    show_field: bool = args.field
    show_stack: bool = args.stack
    show_command: bool = args.command
    operation_count = 0
    operation_limit: int = args.limit if args.limit else 0
    if operation_limit > 0:
      try: # Windows
        from msvcrt import getch
      except ImportError: # Other OS
        def getch():
          import sys
          import tty
          import termios
          fd = sys.stdin.fileno()
          old = termios.tcgetattr(fd)
          try:
            tty.setraw(fd)
            return sys.stdin.read(1)
          finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    command_names = [
      '0p: push(count)', #0
      '1p: push(1)',
      '2p: push(2)',
      '3p: push(3)',
      '4p: push(4)',
      '5p: push(5)',
      '6p: push(6)',
      '7p: push(7)',
      '8p: push(8)',
      'xp: push(sum)',
      '0l: pop', #10
      '1l: positive',
      '2l: dup',
      '3l: add',
      '4l: sub',
      '5l: multi',
      '6l: div',
      '7l: mod',
      '8l: perform(l)',
      '9l: reset(l)',
      '0r: push0', #20
      '1r: not',
      '2r: roll',
      '3r: in(n)',
      '4r: in(c)',
      '5r: out(n)',
      '6r: out(c)',
      '7r: skip',
      '8r: perform(r)',
      '9r: reset(r)',
      'f: swap', #30
      'no: noop',
      'rv: reverse',
      'e: command error'
    ]

    run_time = 0

  height = len(field)
  width = len(field[0])
  operations_length = len(operations)
  range_height = range(height)
  range_width = range(width)


  current_revealed = [[False] * width for _ in range_height]
  ever_revealed = [[False] * width for _ in range_height]
  ever_rest_cells = height * width - mines
  ever_rest_mines = mines
  flagged = [[False] * width for _ in range_height]
  flag_mode = False

  operation_pointer = -1
  opration_to_perform = None

  input_from_stdin = args.input == None
  if not input_from_stdin:
    recent_input = open(args.input, encoding='utf-8').read()
  elif args.echo != None:
    input_from_stdin = False
    recent_input = args.echo
  else:
    recent_input = ''

  stack = []
  stack_append = stack.append
  stack_pop = stack.pop
  stack_insert = stack.insert
  stack_clear = stack.clear

  int_re = re.compile(r'\s*(-?\d+)(.*)', flags=re.ASCII | re.DOTALL)

  def reveal(x: int, y: int, is_mine: bool):
    nonlocal current_revealed, ever_revealed, ever_rest_cells, ever_rest_mines
    current_revealed[x][y] = True
    flagged[x][y] = False
    if not ever_revealed[x][y]:
      ever_revealed[x][y] = True
      if is_mine:
        ever_rest_mines -= 1
      else:
        ever_rest_cells -= 1
  
  def open_recursively(cell: Tuple[int, int], return_sum: bool) -> int:
    ret = 0
    cells = [cell]
    cells_append = cells.append
    cells_pop = cells.pop
    while(len(cells) > 0):
      o_x, o_y = cells_pop()
      for i in range(max(0, o_x - 1), min(height, o_x + 2)): #min(height - 1, o_x + 1) + 1)
        for j in range(max(0, o_y - 1), min(width, o_y + 2)):
          if not current_revealed[i][j]:
            cell_number = field[i][j]
            ret += cell_number if return_sum else 1
            i_j = (i, j)
            reveal(i, j, False)
            if cell_number == 0:
              cells_append(i_j)
    return ret

  def perform_operation(x: int, y: int, right_clicked: bool) -> int:
    nonlocal current_revealed, ever_revealed, ever_rest_cells, ever_rest_mines, flagged, stack, operation_pointer, recent_input, opration_to_perform, stack_append
    if debug_mode:
      nonlocal output_debug
    current_number = field[x][y]
    right_clicked ^= flag_mode
    if current_revealed[x][y]: # revealed
      if right_clicked:
        if current_number == 0: #command-0r (push 0)
          stack_append(0)
          return 20
        else: # number > 0
          flagged_count = 0
          not_revealed_count = 0
          not_revealed_0_list = []
          not_revealed_list = []
          contain_mine = False
          for i in range(max(0, x - 1), min(height, x + 2)):
            for j in range(max(0, y - 1), min(width, y + 2)):
              if flagged[i][j]:
                flagged_count += 1
              elif not current_revealed[i][j]:
                not_revealed_count += 1
                i_j = (i, j)
                i_j_command = field[i][j]
                if i_j_command == 9:
                  contain_mine = True
                elif i_j_command > 0:
                  not_revealed_list.append(i_j)
                else:
                  not_revealed_0_list.append(i_j)
          if not_revealed_count > 0 and flagged_count == current_number:
            if contain_mine: #command-9r (reset game & stack)
              stack_clear()
              current_revealed = [[False] * width for _ in range_height]
              flagged = [[False] * width for _ in range_height]
              return 29
            else: #command-xp (push sum of revealed numbers)
              reveal_sum = 0
              for cell in not_revealed_list:
                c_x, c_y = cell
                reveal(c_x, c_y, False)
                reveal_sum += field[c_x][c_y] # must precede 0s.
              for cell in not_revealed_0_list:
                reveal_sum += open_recursively(cell, True)
              stack_append(reveal_sum)
              return 9
          elif current_number == 1: #command-1r (top == 0 ? 1 : 0)
            if len(stack) > 0:
              stack_append(1 if stack_pop() == 0 else 0)
              return 21
          elif current_number == 2: #command-2r (roll top p1 items p0 times)
            if len(stack) > 1:
              roll_depth = stack[-2]
              if abs(roll_depth) + 1 < len(stack):
                roll_time = stack_pop()
                stack_pop()
                if roll_depth > 0:
                  roll_time_mod = roll_time % roll_depth
                  insert_index = len(stack) - roll_depth
                  roll_items = stack[-roll_time_mod:]
                  del stack[-roll_time_mod:]
                  stack[insert_index:insert_index] = roll_items
                elif roll_depth < 0:
                  roll_time_mod = roll_time % -roll_depth
                  insert_index = -roll_depth - roll_time_mod
                  roll_items = stack[:roll_time_mod]
                  del stack[:roll_time_mod]
                  stack[insert_index:insert_index] = roll_items
                return 22
          elif current_number == 3: #command-3r (input as integer)
            if input_from_stdin:
              recent_input += stdin.read()
            read_match = re.fullmatch(int_re, recent_input)
            if read_match != None:
              stack_append(int(read_match[1]))
              recent_input = read_match[2]
              return 23
          elif current_number == 4: #command-4r (input as char)
            if input_from_stdin:
              recent_input += stdin.read()
            if len(recent_input) > 0:
              c, recent_input = recent_input[0], recent_input[1:]
              stack_append(ord(c))
              return 24
          elif current_number == 5: #command-5r (output top as integer)
            if len(stack) > 0:
              p = stack_pop()
              print(p, end='', flush=True)
              if debug_mode:
                output_debug += str(p)
              return 25
          elif current_number == 6: #command-6r (output top as char)
            if len(stack) > 0:
              p = stack[-1]
              if p > -1 and p < 0x110000:
                c = chr(stack_pop())
                print(c, end='', flush=True)
                if debug_mode:
                  output_debug += c
                return 26
          elif current_number == 7: #command-7r (skip p operations)
            if len(stack) > 0:
              operation_pointer = (operation_pointer + stack_pop()) % operations_length
              return 27
          elif current_number == 8: #command-8r (perform right click(p1, p0))
            if len(stack) > 1:
              opration_to_perform = (stack_pop() % height, stack_pop() % width, True) # inverted.
              return 28
      else: # left-clicked revealed
        if current_number == 0: #command-0l (pop)
          if len(stack) > 0:
            stack_pop()
            return 10
        elif current_number == 1: #command-1l (p > 0 ? 1 : 0)
          if len(stack) > 0:
            stack_append(1 if stack_pop() > 0 else 0)
            return 11
        elif current_number == 2: #command-2l (duplicate top)
          if len(stack) > 0:
            stack_append(stack[-1])
            return 12
        elif current_number == 3: #command-3l (p1 + p0)
          if len(stack) > 1:
            stack_append(stack_pop() + stack_pop())
            return 13
        elif current_number == 4: #command-4l (p1 - p0)
          if len(stack) > 1:
            stack_append(-stack_pop() + stack_pop())
            return 14
        elif current_number == 5: #command-5l (p1 * p0)
          if len(stack) > 1:
            stack_append(stack_pop() * stack_pop())
            return 15
        elif current_number == 6: #command-6l (p1 / p0)
          if len(stack) > 1 and stack[-1] != 0:
            p0, p1 = stack_pop(), stack_pop()
            stack_append(p1 // p0)
            return 16
        elif current_number == 7: #command-7l (p1 % p0)
          if len(stack) > 1 and stack[-1] != 0:
            p0, p1 = stack_pop(), stack_pop()
            stack_append(p1 % p0)
            return 17
        elif current_number == 8: #command-8l (perform left click(p1, p0))
          if len(stack) > 1:
            opration_to_perform = (stack_pop() % height, stack_pop() % width, False) # inverted.
            return 18
    else: # not revealed
      if right_clicked: #command-f (swap top 2 items)
        flagged[x][y] = not flagged[x][y]
        if len(stack) > 1:
          stack[-1], stack[-2] = stack[-2], stack[-1]
          return 30
      elif flagged[x][y]: # left-clicked flagged
        return 31
      else: # left-clicked not flagged
        if current_number == 0: #command-0n (push the number of revealed(>=1))
          reveal_count = open_recursively((x, y), False)
          stack_append(reveal_count)
          return 0
        elif current_number == 9: #command-9l (reset game)
          reveal(x, y, True)
          current_revealed = [[False] * width for _ in range_height]
          flagged = [[False] * width for _ in range_height]
          return 19
        else: #command-1n-8n (push number)
          reveal(x, y, False)
          stack_append(current_number)
          return current_number

    return -1

  while ever_rest_cells > 0 and ever_rest_mines > 0:
    if debug_mode:
      operation_count += 1
      run_start_time = perf_counter_ns()
    if opration_to_perform != None:
      op_x, op_y, op_right = opration_to_perform
      opration_to_perform = None
    else:
      operation_pointer = (operation_pointer + 1) % operations_length
      command_adress = operations[operation_pointer]
      if command_adress == False:
        if debug_mode:
          if show_command:
            print('**command**')
            print('--blank line noop--')
            print()
        continue
      elif command_adress == True: #command-rv (reverse stack)
        flag_mode = not flag_mode
        stack.reverse()
        if debug_mode:
          if show_command:
            print('**command**')
            print(f'exec "{command_names[32]}"')
            print()
          if show_stack:
            print('**stack**')
            print(stack)
            print()
        continue
      else:
        op_x, op_y, op_right = command_adress

    command_number = perform_operation(op_x, op_y, op_right)

    if debug_mode:
      run_time += perf_counter_ns() - run_start_time
      if show_command:
        print('**command**')
        print(f'exec "{command_names[command_number]}" at ({op_y}, {op_x}) by {"right" if op_right else "left"} in {"flag" if flag_mode else "normal"} mode')
        print()
      if show_stack:
        print('**stack**')
        print(stack)
        print()
      if show_field:
        print('**field**')
        for i in range_height:
          for j in range_width:
            number = field[i][j]
            print('F' if flagged[i][j] else ('#' if not current_revealed[i][j] else (number if number > 0 else '.')), end=' ')
          print()
        print()
      if operation_limit > 0 and operation_count % operation_limit == 0:
        print('**whole output start**')
        print(output_debug)
        print('**whole output end**')
        print(f'operaion count: {operation_count}')
        print(f'Continue to press [Enter] or exit to press any other key.')
        if getch() != '\r':
          break

  if debug_mode:
    print()
    print('**whole output start**')
    print(output_debug)
    print('**whole output end**')
    print(f'operaion count: {operation_count}')
    print()
    print(f'run: {run_time / 1000000}ms')

def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('program_path', help='Program path', type=str)
  arg_parser.add_argument('-i', '--input', help='Input file path', type=str)
  arg_parser.add_argument('-e', '--echo', help='String to echo to input', type=str)
  arg_parser.add_argument('-d', '--debug', help="Debug mode", action="store_true")
  arg_parser.add_argument('-c', '--command', help="Show command each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-s', '--stack', help="Show stack each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-f', '--field', help="Show field each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-l', '--limit', help="Limit operation count to perform at once (require debug mode)", type=int)
  arg_parser.add_argument('-V', '--version', action='version', version=__version__)
  args = arg_parser.parse_args()

  filename = args.program_path
  run(*parse_code(filename, args), args)

if __name__ == "__main__":
  main()
