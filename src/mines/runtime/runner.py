from collections import deque
from collections.abc import Callable
from typing import NamedTuple, TextIO

from mines.player.operation import Operation
from mines.player.player import Player
from mines.program.program import Program
from mines.runtime.command_selector import select_command
from mines.runtime.command_type import CommandErrorType, CommandType
from mines.runtime.input_buffer import InputBuffer, InputSource
from mines.runtime.operation_pointer import OperationPointer
from mines.runtime.output_buffer import OutputBuffer
from mines.runtime.runtime_state import RuntimeState
from mines.runtime.stack import Stack


class StepResult(NamedTuple):
    operation: Operation
    command_type: CommandType
    command_error_type: CommandErrorType | None


StepListener = Callable[[StepResult], None]


class Runner:
    __runtime_state: RuntimeState
    __step_listener: StepListener | None

    def __init__(
        self,
        program: Program,
        input_source: InputSource,
        output_io: TextIO,
        step_listener: StepListener | None,
    ) -> None:
        self.__runtime_state = RuntimeState(
            Player(program.cell_digits),
            OperationPointer(program.operation_list),
            deque(),
            Stack(),
            InputBuffer(input_source),
            OutputBuffer(output_io),
        )
        self.__step_listener = step_listener

    def __get_next_operation(self) -> Operation:
        runtime_state = self.__runtime_state
        if len(runtime_state.operation_queue) == 0:
            runtime_state.operation_queue.append(
                runtime_state.operation_pointer.request_operation(),
            )
        return runtime_state.operation_queue.popleft()

    def __process_next_operation(self) -> bool:
        runtime_state = self.__runtime_state
        player_state = runtime_state.player.get_player_state()

        if player_state.game_status == "cleared":
            return False

        operation = self.__get_next_operation()
        runtime_state.player.perform_operation(operation)
        command = select_command(operation, runtime_state.player)
        command_error_type = (
            command.validate(runtime_state) if command.validate else None
        )
        if command_error_type is None:
            command.execute(runtime_state)

        if self.__step_listener:
            step_result = StepResult(operation, command.name, command_error_type)
            self.__step_listener(step_result)

        return True

    def run(self) -> None:
        while self.__process_next_operation():
            pass

    def get_runtime_state(self) -> RuntimeState:
        return self.__runtime_state
