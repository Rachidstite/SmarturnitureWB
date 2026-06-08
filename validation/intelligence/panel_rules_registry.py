from validation.intelligence.structural.structural_rules import (
    get_structural_rules,
)


class PanelRulesRegistry:

    @staticmethod
    def get_rules():

        return (
            get_structural_rules()
        )
