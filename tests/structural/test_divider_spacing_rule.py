import unittest

from manufacturing.panel_spec import PanelSpec
from shared.roles import NodeRole

from validation.intelligence.structural.divider_spacing_rule import (
    DividerSpacingRule,
)


class TestDividerSpacingRule(
    unittest.TestCase
):

    def test_warns_for_large_opening(self):

        panel = PanelSpec(
            identity="TEST",
            role=NodeRole.SHELF,
            width=500,
            height=500,
            thickness=18,
            material="MDF",
            span=1400,
        )

        result = DividerSpacingRule().validate(
            panel,
            None
        )

        self.assertFalse(
            result.passed
        )

        self.assertEqual(
            result.code,
            "DIVIDER_RECOMMENDED"
        )


if __name__ == "__main__":
    unittest.main()
