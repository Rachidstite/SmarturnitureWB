from dataclasses import dataclass

SYSTEM32_PITCH = 32

@dataclass(frozen=True)
class System32Rule:
    hinge_line: float = 37.0
    shelf_pin_pitch: float = 32.0
    shelf_pin_diameter: float = 5.0
    minifix_offset: float = 37.0
    minifix_diameter: float = 15.0
    confirmat_offset: float = 37.0

class System32Engine:

    @staticmethod
    def shelf_positions(height):
        pos = []
        y = 64

        while y < height - 64:
            pos.append(y)
            y += SYSTEM32_PITCH

        return pos

    @staticmethod
    def hinge_positions(height):

        top = 100
        bottom = height - 100

        if height < 900:
            return [top, bottom]

        middle = height / 2

        return [top, middle, bottom]

    @staticmethod
    def minifix_positions(length):

        start = 37
        end = length - 37

        return [start, end]
