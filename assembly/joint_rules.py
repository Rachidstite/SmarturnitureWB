from dataclasses import dataclass

@dataclass
class JointRule:
    parent_role: str
    child_role: str
    joint_type: str
    minifix_count: int
    dowel_count: int


RULES = [

    JointRule(
        "SIDE_PANEL",
        "TOP_PANEL",
        "MINIFIX",
        3,
        2
    ),

    JointRule(
        "SIDE_PANEL",
        "BOTTOM_PANEL",
        "MINIFIX",
        3,
        2
    ),

    JointRule(
        "DIVIDER",
        "TOP_PANEL",
        "MINIFIX",
        3,
        2
    ),

    JointRule(
        "DIVIDER",
        "BOTTOM_PANEL",
        "MINIFIX",
        3,
        2
    )
]
