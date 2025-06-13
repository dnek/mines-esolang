from mines.player.operation import Operation


class OperationPointer:
    __operation_list: list[Operation]
    __index: int

    def __init__(self, operation_list: list[Operation]) -> None:
        self.__operation_list = operation_list
        self.__index = 0

    def advance(self, n: int) -> None:
        self.__index = (self.__index + n) % len(self.__operation_list)

    def request_operation(self) -> Operation:
        operation = self.__operation_list[self.__index]
        self.advance(1)
        return operation
