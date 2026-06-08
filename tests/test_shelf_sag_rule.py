import unittest

from manufacturing.panel_spec import PanelSpec
from shared.roles import NodeRole

from validation.intelligence.structural.shelf_sag_rule import (
    ShelfSagRule,
)


class TestShelfSagRule(
    unittest.TestCase
):

    def test_warns_for_long_18mm_shelf(self):

        panel = PanelSpec(
            identity="TEST",
            role=NodeRole.SHELF,
            width=500,
            height=500,
            thickness=18,
            material="MDF",
            span=1000,
        )

        result = ShelfSagRule().validate(
            panel,
            None
        )

        self.assertFalse(
            result.passed
        )

        self.assertEqual(
            result.code,
            "SHELF_SAG"
        )


if __name__ == "__main__":
    unittest.main()
