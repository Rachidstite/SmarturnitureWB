from dataclasses import dataclass


@dataclass
class OffcutClassification:
    """
    Offcut reusability classification contract.
    """

    offcut_id: str

    reusable: bool = True

    reason: str = ""
