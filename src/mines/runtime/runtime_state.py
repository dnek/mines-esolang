from collections import deque
from dataclasses import dataclass

from mines.player.operation import Operation
from mines.player.player import Player
from mines.runtime.input_buffer import InputBuffer
from mines.runtime.operation_pointer import OperationPointer
from mines.runtime.output_buffer import OutputBuffer
from mines.runtime.stack import Stack


@dataclass
class RuntimeState:
    player: Player
    operation_pointer: OperationPointer
    operation_queue: deque[Operation]
    stack: Stack
    input_buffer: InputBuffer
    output_buffer: OutputBuffer
