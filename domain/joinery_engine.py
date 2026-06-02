from dataclasses import dataclass

@dataclass(frozen=True)
class Connector:
    kind: str
    x: float
    y: float
    z: float

class JoineryEngine:

    @staticmethod
    def minifix_for_panel(width, depth):

        return [
            Connector("MINIFIX", 37, depth/2, 0),
            Connector("MINIFIX", width-37, depth/2, 0)
        ]

    @staticmethod
    def confirmat_for_panel(width, depth):

        return [
            Connector("CONFIRMAT", 37, depth/2, 0),
            Connector("CONFIRMAT", width-37, depth/2, 0)
        ]
