from dataclasses import dataclass, field


@dataclass
class RemainingRegion:
    """
    Free rectangular nesting region contract.
    """

    id: str

    x: float

    y: float

    width: float

    height: float

    source_sheet: str

    area: float = field(
        init=False,
    )

    def __post_init__(
        self,
    ):
        self.area = (
            self.width
            * self.height
        )
