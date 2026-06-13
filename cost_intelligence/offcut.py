from dataclasses import dataclass, field


@dataclass
class Offcut:
    """
    Reusable sheet remnant contract.
    """

    id: str

    material: str

    thickness: float

    width: float

    height: float

    source_sheet: str

    reusable: bool = True

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
