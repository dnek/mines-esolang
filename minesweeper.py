import argparse
from collections import deque
from re import compile as re_compile, fullmatch, sub
from time import perf_counter
from typing import List, Tuple

def parse_code(filename: str):
  raw_code = open(filename, encoding='utf-8').read().split(sep='\n')
  line_re = re_compile(r'[^.*\-0-9,]+')
  formatted_code = list(map(lambda line: sub(line_re, '', line), raw_code))
  width = len(formatted_code[0])
  if width == 0:
    raise NameError('The first row of field is empty.')
  height = 0

  field = [] #[[bool]]
  open_set_list = [] #[set]
  open_set_address = [] #[[int]]
  commands = [] #[(int, int)]

  row_re = re_compile(r'[.*]{{{width}}}'.format(width=width))
  command_re = re_compile(r'(-?[0-9]*),(-?[0-9]*)')

  def construct_open_set():
    nonlocal open_set_list, open_set_address
    open_set_address = [[-1] * width for _ in range(height)]
    def is_0(x: int, y: int):
      for i in range(max(0, x - 1), min(height - 1, x + 1) + 1):
        for j in range(max(0, y - 1), min(width - 1, y + 1) + 1):
          if field[i][j]:
            return False
      return True
    for x in range(height):
      for y in range(width):
        if open_set_address[x][y] == -1 and is_0(x, y):
          open_set_list_index = len(open_set_list)
          open_set_address[x][y] = open_set_list_index
          x_y = (x, y)
          open_set = set([x_y])
          search_que = deque([x_y])
          open_set_add = open_set.add
          search_que_append = search_que.append
          while(len(search_que)):
            o_x, o_y = search_que.pop()
            for i in range(max(0, o_x - 1), min(height - 1, o_x + 1) + 1):
              for j in range(max(0, o_y - 1), min(width - 1, o_y + 1) + 1):
                if open_set_address[i][j] == -1:
                  i_j = (i, j)
                  open_set_add(i_j)
                  if is_0(i, j):
                    open_set_address[i][j] = open_set_list_index
                    search_que_append(i_j)
          open_set_list.append(open_set)

  def parse_command(line: str) -> (int, int):
    if len(line) == 0:
      return None
    else:
      command_match = fullmatch(command_re, line)
      if not command_match:
        raise NameError(f"Command '{line}' is inconsistent.")
      return (int(command_match[2]), int(command_match[1])) # inverted.

  parsing_field = True
  field_append = field.append
  commands_append = commands.append
  for line in formatted_code:
    if parsing_field:
      if not fullmatch(row_re, line):
        parsing_field = False
        height = len(field)
        if height == 0:
          raise NameError('There is no row of field.')
        construct_open_set()
        commands_append(parse_command(line))
      else:
        field_append([c == '*' for c in line])
    else:
      commands_append(parse_command(line))
  return field, open_set_list, open_set_address, commands

def run(field: List[List[bool]],
    open_set_list: List[set],
    open_set_address: List[List[int]],
    commands: List[Tuple[int, int]]):
  print('**field**')
  for i in field:
    print(i)
  print('**open set list**')
  for i in open_set_list:
    print(i)
  print('**open set address**')
  for i in open_set_address:
    print(i)
  print('**commands**')
  for i in commands:
    print(i)

def main():
  arg_parser = argparse.ArgumentParser()
  arg_parser.add_argument('program_path', help='Program path', type=str)
  args = arg_parser.parse_args()
  filename = args.program_path
  start_time = perf_counter()
  parsed_data = parse_code(filename)
  run(*parsed_data)
  end_time = perf_counter()
  print('time(s):', end_time - start_time)

if __name__ == "__main__":
  main()