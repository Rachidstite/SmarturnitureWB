import unittest

from manufacturing.panel_spec import PanelSpec
from shared.roles import NodeRole

from domain.manufacturing_ops import EdgeDrill

from validation.manufacturing_feasibility_validator import (
    ManufacturingFeasibilityValidator
)


class TestManufacturingFeasibilityValidator(unittest.TestCase):

    def test_panel_too_small_for_minifix(self):

        spec = PanelSpec(
            identity="MINIFIX_FAIL",
            role=NodeRole.SHELF,
            width=50,
            height=300,
            thickness=18,
            material="MDF",
            cnc_operations=[
                EdgeDrill(
                    x=64,
                    z=9,
                    diameter=8,
                    depth=30,
                    edge="TOP"
                )
            ]
        )

        issues = (
            ManufacturingFeasibilityValidator()
            .validate([spec])
        )

        codes = {i.code for i in issues}

        self.assertIn(
            "PANEL_TOO_SMALL_FOR_MINIFIX",
            codes
        )


if __name__ == "__main__":
    unittest.main()
