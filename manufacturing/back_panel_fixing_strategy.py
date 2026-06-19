from enum import Enum


class BackPanelFixingStrategy(str, Enum):
    GROOVE = "GROOVE"
    SCREWED = "SCREWED"
    STAPLED = "STAPLED"
