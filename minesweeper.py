import argparse
from collections import deque
import re
from sys import stdin
from time import perf_counter
from typing import List, Set, Tuple

def parse_code(filename: str):
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
  open_set_list = [] #[set]
  open_set_address = [] #[[int]]
  commands = [] #[(int, int, bool)]

  row_re = re.compile(r'[.*]{{{width}}}'.format(width=width))
  command_re = re.compile(r'(0|-?[1-9][0-9]*)([,;])(0|-?[1-9][0-9]*)')

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

  def construct_open_set():
    nonlocal open_set_list, open_set_address
    open_set_address = [[-1] * width for _ in range(height)]
    open_set_list_append = open_set_list.append
    for x in range(height):
      for y in range(width):
        if open_set_address[x][y] == -1 and field[x][y] == 0:
          open_set_list_index = len(open_set_list)
          open_set_address[x][y] = open_set_list_index
          x_y = (x, y)
          open_set = set([x_y])
          search_que = deque([x_y])
          open_set_add = open_set.add
          search_que_append = search_que.append
          search_que_pop = search_que.pop
          while(len(search_que) > 0):
            o_x, o_y = search_que_pop()
            for i in range(max(0, o_x - 1), min(height - 1, o_x + 1) + 1):
              for j in range(max(0, o_y - 1), min(width - 1, o_y + 1) + 1):
                if open_set_address[i][j] == -1:
                  i_j = (i, j)
                  open_set_add(i_j)
                  open_set_address[i][j] = open_set_list_index
                  if field[i][j] == 0:
                    search_que_append(i_j)
          open_set_list_append(open_set)

  def parse_command(line: str) -> (int, int, bool):
    if len(line) == 0:
      return None
    else:
      command_match = re.fullmatch(command_re, line)
      if not command_match:
        raise NameError(f"Command '{line}' is inconsistent.")
      return (int(command_match[3]) % height, int(command_match[1]) % width, command_match[2] == ';') # inverted.

  parsing_field = True
  is_mine_append = is_mine.append
  commands_append = commands.append
  for line in formatted_code:
    if parsing_field:
      if not re.fullmatch(row_re, line):
        parsing_field = False
        height = len(is_mine)
        if height == 0:
          raise NameError('There is no row of field.')
        construct_field()
        construct_open_set()
        commands_append(parse_command(line))
      else:
        parsed_line = [c == '*' for c in line]
        mines += parsed_line.count(True)
        is_mine_append(parsed_line)
    else:
      commands_append(parse_command(line))
  return field, mines, open_set_list, open_set_address, commands

def run(field: List[List[int]],
    mines: int,
    open_set_list: List[Set[Tuple[int, int]]],
    open_set_address: List[List[int]],
    commands: List[Tuple[int, int, bool]]):
  
  debug_mode: bool = args.debug
  if debug_mode:
    output_debug = ''
    show_field: bool = args.field
    show_stack: bool = args.stack
    show_command: bool = args.command
    command_limit: int = args.limit if args.limit else -1
    command_names = [
      '0: push',
      '1: not',
      '2: in(n)',
      '3: in(c)',
      '4: out(n)',
      '5: out(c)',
      '6: pick',
      '7: insert',
      '8: skip',
      '9: reset',
      '0r: dup',
      '1r: pop',
      '2r: add',
      '3r: sub',
      '4r: mul',
      '5r: div',
      '6r: mod',
      '7r: positive',
      '8r: exec',
    ]

  height = len(field)
  width = len(field[0])
  command_length = len(commands)


  current_revealed = [[False] * width for _ in range(height)]
  ever_revealed = [[False] * width for _ in range(height)]
  ever_rest_cells = height * width - mines
  ever_rest_mines = mines
  stack = []
  command_pointer = -1
  recent_input = ''
  command_to_exec = None

  stack_append = stack.append
  stack_pop = stack.pop
  stack_insert = stack.insert

  def in_range(index: int) -> bool:
    return len(stack) > ((-index - 1) if index < 0 else index)
  def in_range_1(index: int) -> bool:
    return len(stack) - 1 > ((-index - 1) if index < 0 else index)

  int_re = re.compile(r'\s*(-?\d+)(.*)', flags=re.ASCII | re.DOTALL)

  def exexute_command(x: int, y: int):
    nonlocal current_revealed, ever_revealed, ever_rest_cells, ever_rest_mines, stack, command_pointer, recent_input, command_to_exec, stack_append
    if debug_mode:
      nonlocal output_debug
    current_command = field[x][y]
    if current_revealed[x][y]:
      if current_command == 0: #command-0r (duplicate top)
        if len(stack) > 0:
          stack_append(stack[-1])
      elif current_command == 1: #command-1r (pop)
        if len(stack) > 0:
          stack_pop()
      elif current_command == 2: #command-2r (p1 + p0)
        if len(stack) > 1:
          stack_append(stack_pop() + stack_pop())
      elif current_command == 3: #command-3r (p1 - p0)
        if len(stack) > 1:
          stack_append(-stack_pop() + stack_pop())
      elif current_command == 4: #command-4r (p1 * p0)
        if len(stack) > 1:
          stack_append(stack_pop() * stack_pop())
      elif current_command == 5: #command-5r (p1 / p0)
        if len(stack) > 1 and stack[-1] != 0:
          p0, p1 = stack_pop(), stack_pop()
          stack_append(p1 // p0)
      elif current_command == 6: #command-6r (p1 % p0)
        if len(stack) > 1 and stack[-1] != 0:
          p0, p1 = stack_pop(), stack_pop()
          stack_append(p1 % p0)
      elif current_command == 7: #command-7r (p > 0 ? 1 : 0)
        if len(stack) > 0:
          stack_append(1 if stack_pop() > 0 else 0)
      elif current_command == 8: #command-8r (exec open[p1][p0])
        if len(stack) > 1:
          command_to_exec = (stack_pop() % len(height), stack_pop() % len(height)) # inverted.

    elif current_command == 0: #command-0 (push the number of revealed(>=0))
      reveal_count = -1
      for c_x, c_y in open_set_list[open_set_address[x][y]]:
        if not current_revealed[c_x][c_y]:
          current_revealed[c_x][c_y] = True
          reveal_count += 1
          if not ever_revealed[c_x][c_y]:
            ever_revealed[c_x][c_y] = True
            ever_rest_cells -= 1
      stack_append(reveal_count)

    elif current_command == 9: #command-9 (restart game)
      current_revealed[x][y] = True
      if not ever_revealed[x][y]:
        ever_revealed[x][y] = True
        ever_rest_mines -= 1
      current_revealed = [[False] * width for _ in range(height)]

    else:
      current_revealed[x][y] = True
      if not ever_revealed[x][y]:
        ever_revealed[x][y] = True
        ever_rest_cells -= 1

      if current_command == 1: #command-1 (top == 0 ? 1 : 0)
        if len(stack) > 0:
          stack_append(1 if stack_pop() == 0 else 0)
      elif current_command == 2: #command-2 (input as integer)
        recent_input += stdin.read()
        read_match = re.fullmatch(int_re, recent_input)
        if read_match == None:
          return
        else:
          stack_append(int(read_match[1]))
          recent_input = read_match[2]
      elif current_command == 3: #command-3 (input as char)
        recent_input += stdin.read()
        if len(recent_input) > 0:
          c, recent_input = recent_input[0], recent_input[1:]
          stack_append(ord(c))
      elif current_command == 4: #command-4 (output top as integer)
        if len(stack) > 0:
          p = stack_pop()
          print(p, end='', flush=True)
          if debug_mode:
            output_debug += str(p)
      elif current_command == 5: #command-5 (output top as char)
        if len(stack) > 0:
          p = stack[-1]
          if p > -1 and p < 0x110000:
            c = chr(stack_pop())
            print(c, end='', flush=True)
            if debug_mode:
              output_debug += c
      elif current_command == 6: #command-6 (pick up item at p0)
        if len(stack) > 1:
          p = stack_pop()
          if p < 0:
            i = min(-p - 1, len(stack) - 1)
            stack_append(stack_pop(i))
          elif p > 0:
            i = max(-p - 1, -len(stack))
            stack_append(stack_pop(i))
      elif current_command == 7: #command-7 (insert p1 into p0)
        if len(stack) > 1:
          p = stack_pop()
          if p != 0:
            p1 = stack_pop()
            if p > 0:
              stack_insert(-p, p1)
            else:
              stack_insert(-p - 1, p1)
      elif current_command == 8: #command-8 (skip p commands)
        if len(stack) > 0:
          command_pointer = (command_pointer + stack_pop()) % command_length

  while ever_rest_cells > 0 and ever_rest_mines > 0:
    if debug_mode:
      if command_limit == 0:
        print('Command limit exceeded.')
        break
      elif command_limit > 0:
        command_limit -= 1
    if command_to_exec != None:
      com_x, com_y = command_to_exec
      command_to_exec = None
    else:
      command_pointer = (command_pointer + 1) % command_length
      command_adress = commands[command_pointer]
      if command_adress == None:
        if debug_mode:
          if show_command:
            print('nop')
            print()
        continue
      com_x, com_y, com_right = command_adress

    if debug_mode:
      if show_field:
        print('**field**')
        for i in range(height):
          for j in range(width):
            number = field[i][j]
            print((number if number > 0 else ' ') if current_revealed[i][j] else '#', end=' ')
          print()
        print()
      if show_stack:
        print('**stack**')
        print(stack)
        print()
      if show_command:
        print(f'exec "{command_names[field[com_x][com_y] + (10 if current_revealed[com_x][com_y] else 0)]}" at ({com_y}, {com_x})')
        print()

    exexute_command(com_x, com_y)

  if debug_mode:
    print()
    if show_field:
      print('**field**')
      for i in range(height):
        for j in range(width):
          number = field[i][j]
          print((number if number > 0 else ' ') if current_revealed[i][j] else '#', end=' ')
        print()
      print()
    if show_stack:
      print('**stack**')
      print(stack)
      print()
    print('**whole output start**')
    print(output_debug)
    print('**whole output end**')
    print()

def main():
  filename = args.program_path
  debug_mode = args.debug
  if debug_mode:
    parse_start_time = perf_counter()
  parsed_data = parse_code(filename)
  if debug_mode:
    parse_end_time = perf_counter()
    print('   ', end='')
    for i in range(len(parsed_data[0][0])):
      print(str(i).rjust(3), end='')
    print()
    for i, l in enumerate(parsed_data[0]):
      print(str(i).rjust(3), l)
    run_start_time = perf_counter()
  run(*parsed_data)
  if debug_mode:
    end_time = perf_counter()
    print(f'parse: {parse_end_time - parse_start_time}s, run: {end_time - run_start_time}s')

if __name__ == "__main__":
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('-d', '--debug', help="Debug mode", action="store_true")
  arg_parser.add_argument('-f', '--field', help="Show field each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-s', '--stack', help="Show stack each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-c', '--command', help="Show command each phase (require debug mode)", action="store_true")
  arg_parser.add_argument('-l', '--limit', help="Limit command execution count (require debug mode)", type=int)
  arg_parser.add_argument('program_path', help='Program path', type=str)
  args = arg_parser.parse_args()
  main()
