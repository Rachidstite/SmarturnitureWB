from dataclasses import dataclass

SYSTEM_PITCH = 32.0
FRONT_SETBACK = 37.0

class System32Engine:

    @staticmethod
    def hinge_positions(door_height):

        if door_height <= 900:
            return [100, door_height - 100]

        elif door_height <= 1600:
            return [100, door_height / 2, door_height - 100]

        elif door_height <= 2400:
            return [
                100,
                door_height * 0.33,
                door_height * 0.66,
                door_height - 100
            ]

        else:
            return [
                100,
                door_height * 0.25,
                door_height * 0.50,
                door_height * 0.75,
                door_height - 100
            ]

    @staticmethod
    def minifix_positions(panel_length: float):

        if panel_length < 300:
            return [64]

        if panel_length < 700:
            return [64, panel_length - 64]

        return [
            64,
            panel_length / 2,
            panel_length - 64
        ]

    @staticmethod
    def shelf_pin_positions(panel_height: float):

        positions = []

        z = 64

        while z < panel_height - 64:
            positions.append(z)
            z += SYSTEM_PITCH

        return positions

