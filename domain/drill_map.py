from dataclasses import dataclass

@dataclass(frozen=True)
class DrillPoint:
    x: float
    y: float
    z: float

    diameter: float
    depth: float

    operation: str

class DrillMap:

    def __init__(self):
        self.points = []

    def add(self, point):
        self.points.append(point)

    def all_points(self):
        return list(self.points)

    def count(self):
        return len(self.points)
