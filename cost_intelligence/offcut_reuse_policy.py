from dataclasses import dataclass


@dataclass
class OffcutReusePolicy:
    """
    Material-specific offcut reuse threshold contract.
    """

    material: str

    thickness: float

    min_width: float

    min_height: float

    min_area: float
