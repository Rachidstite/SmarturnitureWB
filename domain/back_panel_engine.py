from dataclasses import dataclass

@dataclass(frozen=True)
class BackPanelRule:
    thickness: float = 8.0
    groove_depth: float = 8.0
    groove_offset: float = 10.0
    groove_clearance: float = 0.2

class BackPanelEngine:

    @staticmethod
    def requires_groove(rule: BackPanelRule):
        return rule.thickness <= 3.5

    @staticmethod
    def groove_width(rule: BackPanelRule):
        return rule.thickness + rule.groove_clearance

    @staticmethod
    def insertion_depth(rule: BackPanelRule):
        return rule.groove_depth

    @staticmethod
    def offset(rule: BackPanelRule):
        return rule.groove_offset
