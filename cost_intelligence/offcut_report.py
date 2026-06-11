from dataclasses import dataclass, field


@dataclass
class OffcutReport:
    """
    Recoverable nesting material report contract.
    """

    offcuts: list = field(
        default_factory=list
    )

    total_offcuts: int = 0

    reusable_offcuts: int = 0

    total_offcut_area: float = 0.0

    largest_offcut_area: float = 0.0

    warnings: list = field(
        default_factory=list
    )
