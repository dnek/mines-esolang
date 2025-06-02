from collections import deque

MIN_ABS_ROLL_DEPTH = 2


class Stack:
    __deque: deque[int]
    __is_reversed: bool

    def __init__(self) -> None:
        self.__deque = deque()
        self.__is_reversed = False

    def __len__(self) -> int:
        return len(self.__deque)

    def __str__(self) -> str:
        return ", ".join(
            [
                str(value)
                for value in (
                    reversed(self.__deque) if self.__is_reversed else self.__deque
                )
            ],
        )

    def peek(self, top_index: int) -> int:
        if self.__is_reversed:
            return self.__deque[top_index]
        return self.__deque[-1 - top_index]

    def get_pops(self, pop_count: int) -> list[int]:
        if self.__is_reversed:
            return [self.__deque.popleft() for _ in range(pop_count)]
        return [self.__deque.pop() for _ in range(pop_count)]

    def push(self, *value: int) -> None:
        if self.__is_reversed:
            self.__deque.extendleft(value)
        else:
            self.__deque.extend(value)

    def reverse(self) -> None:
        self.__is_reversed ^= True

    def roll(self, depth: int, roll_time: int) -> None:
        if abs(depth) < MIN_ABS_ROLL_DEPTH:
            return

        if depth < -1:
            self.reverse()
            self.roll(-depth, roll_time)
            self.reverse()
            return

        roll_time_rem = roll_time % depth

        if roll_time_rem == 0:
            return

        bottoms = self.get_pops(roll_time_rem)
        tops = self.get_pops(depth - roll_time_rem)
        self.push(*reversed(bottoms))
        self.push(*reversed(tops))

    def clear(self) -> None:
        self.__deque.clear()
