import math
from enum import Enum, auto
class NormalizationMode(Enum): FLOOR = auto(); CEIL = auto(); NEAREST = auto()
class DimensionNormalizer:
    @staticmethod
    def round_to_increment(value: float, increment: float, mode: NormalizationMode = NormalizationMode.NEAREST) -> float:
        if mode == NormalizationMode.FLOOR: return math.floor(value / increment) * increment
        elif mode == NormalizationMode.CEIL: return math.ceil(value / increment) * increment
        else: return round(value / increment) * increment
