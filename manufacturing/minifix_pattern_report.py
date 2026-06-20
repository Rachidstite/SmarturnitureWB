from dataclasses import dataclass


@dataclass
class MinifixPatternReport:
    pattern_type: str = ""
    minifix_count: int = 0
    horizontal_count: int = 0
    vertical_count: int = 0
    corner_count: int = 0
    center_count: int = 0
    symmetrical_pattern: bool = False
    pattern_description: str = ""
