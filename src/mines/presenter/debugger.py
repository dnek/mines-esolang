import sys
from io import StringIO
from sys import stderr, stdin

from mines.program.program import Program
from mines.runtime.command_type import CommandType
from mines.runtime.input_buffer import InputSource
from mines.runtime.runner import Runner, StepResult
from mines.view.ansi import Ansi, em
from mines.view.cli_frame_drawer import CliFrameDrawer
from mines.view.input_view import InputView
from mines.view.output_view import OutputView
from mines.view.player_view import PlayerView
from mines.view.prompt import Prompt
from mines.view.step_result_view import StepResultView


class Debugger:
    __operation_count: int
    __last_command_name: CommandType
    __last_stack_str: str
    __last_step_count: int
    __rest_skip_count: int
    __input_view: InputView
    __output_io: StringIO
    __output_view: OutputView

    __runner: Runner

    def __init__(self, program: Program, input_source: InputSource) -> None:
        self.__operation_count = 0
        self.__last_command_name = "noop"
        self.__last_stack_str = "--"
        self.__last_step_count = 100
        self.__rest_skip_count = 0
        self.__input_view = InputView(input_source)
        self.__output_io = StringIO()
        self.__output_view = OutputView(self.__output_io)

        self.__runner = Runner(program, input_source, self.__output_io, self.__step)

    def __del__(self) -> None:
        self.__output_io.close()

    def __draw(self, step_result: StepResult) -> None:
        runtime_state = self.__runner.get_runtime_state()

        player_view = PlayerView(runtime_state.player)

        step_result_view = StepResultView(runtime_state.player, step_result)

        operation_descriptions = [
            f"#{self.__operation_count}",
            step_result_view.get_operation_str(),
        ]

        commands_to_show_last: tuple[CommandType, ...] = (
            "perform(l)",
            "perform(r)",
            "reset(l)",
            "reset(r)",
        )
        if self.__last_command_name in commands_to_show_last:
            operation_descriptions.append(f"by {em(self.__last_command_name)}")

        stack_before_str = str(Ansi(self.__last_stack_str, faint=True))

        cli_frame_drawer = CliFrameDrawer()

        cli_frame_drawer.add_line(player_view.get_board_info_str(), "board")
        cli_frame_drawer.add_line("")
        cli_frame_drawer.add_line(player_view.get_board_str())
        cli_frame_drawer.add_line("")
        cli_frame_drawer.add_line(" ".join(operation_descriptions), "operation")
        cli_frame_drawer.add_line(player_view.get_click_result_str(), "click result")
        cli_frame_drawer.add_line(step_result_view.get_command_str(), "command")
        cli_frame_drawer.add_line(stack_before_str, "stack before")
        cli_frame_drawer.add_line(str(runtime_state.stack), "stack after ")
        cli_frame_drawer.add_line("", "input")
        cli_frame_drawer.add_line(self.__input_view.get_str())
        cli_frame_drawer.add_line("", "output")
        cli_frame_drawer.add_line(self.__output_view.get_str())
        cli_frame_drawer.add_line("")

        cli_frame_drawer.draw_frame()

    def __prompt_step_count(self) -> None:
        message = str(Ansi("enter the step count >>> ", fg=5, bold=True))
        stderr.write(message)
        stderr.flush()
        self.__last_step_count = int(stdin.readline())
        self.__rest_skip_count = self.__last_step_count

    def __rerun_step(self) -> None:
        self.__rest_skip_count = self.__last_step_count

    def __continue(self) -> None:
        self.__rest_skip_count = -1

    def __show_prompt(self) -> None:
        prompt = Prompt()

        prompt.add((" ", "n"), lambda: None, "[space]/[n]ext")
        prompt.add("s", self.__prompt_step_count, "[s]tep N")
        prompt.add("r", self.__rerun_step, f"[r]erun step {self.__last_step_count}")
        prompt.add("c", self.__continue, "[c]ontinue")
        prompt.add("q", lambda: sys.exit(0), "[q]uit\n")

        prompt.show()

    def __step(self, step_result: StepResult) -> None:
        self.__operation_count += 1

        is_cleared = (
            self.__runner.get_runtime_state().player.get_player_state().game_status
            == "cleared"
        )

        if is_cleared:
            self.__draw(step_result)
            stderr.write(str(Ansi("game cleared and exit.\n", fg=2)))
            stderr.flush()
            return

        if self.__rest_skip_count > 0:
            self.__rest_skip_count -= 1

        if self.__rest_skip_count == 0:
            self.__draw(step_result)
            self.__show_prompt()

        self.__last_command_name = step_result.command_type
        self.__last_stack_str = str(self.__runner.get_runtime_state().stack)

    def run(self) -> None:
        self.__runner.run()
