import unittest

from manufacturing.panel_spec import PanelSpec
from validation.panel_spec_validator import PanelSpecValidator
from shared.roles import NodeRole

class TestPanelSpecValidator(unittest.TestCase):

    def test_invalid_dimensions(self):

        spec = PanelSpec(
            identity="TEST",
            role=NodeRole.SHELF,
            width=0,
            height=-1,
            thickness=0,
            material=""
        )

        issues = PanelSpecValidator().validate([spec])

        codes = {i.code for i in issues}

        self.assertIn("WIDTH_INVALID", codes)
        self.assertIn("HEIGHT_INVALID", codes)
        self.assertIn("THICKNESS_INVALID", codes)
        self.assertIn("MATERIAL_MISSING", codes)

if __name__ == "__main__":
    unittest.main()

from domain.manufacturing_ops import FaceDrill

class TestPanelSpecValidatorCNC(unittest.TestCase):

    def test_invalid_drill_parameters(self):

        spec = PanelSpec(
            identity="CNC_TEST",
            role=NodeRole.SHELF,
            width=500,
            height=300,
            thickness=18,
            material="MDF",
            cnc_operations=[
                FaceDrill(
                    x=50,
                    y=50,
                    diameter=0,
                    depth=-5,
                    face="TOP"
                )
            ]
        )

        issues = PanelSpecValidator().validate([spec])

        codes = {i.code for i in issues}

        self.assertIn(
            "DRILL_DIAMETER_INVALID",
            codes
        )

        self.assertIn(
            "DRILL_DEPTH_INVALID",
            codes
        )

from domain.manufacturing_ops import FaceDrill

class TestPanelSpecValidatorBounds(unittest.TestCase):

    def test_drill_out_of_bounds(self):

        spec = PanelSpec(
            identity="BOUNDARY_TEST",
            role=NodeRole.SHELF,
            width=500,
            height=300,
            thickness=18,
            material="MDF",
            cnc_operations=[
                FaceDrill(
                    x=9999,
                    y=9999,
                    diameter=15,
                    depth=12,
                    face="TOP"
                )
            ]
        )

        issues = PanelSpecValidator().validate([spec])

        codes = {i.code for i in issues}

        self.assertIn(
            "DRILL_OUT_OF_BOUNDS",
            codes
        )

from domain.manufacturing_ops import EdgeDrill

class TestPanelSpecValidatorFeasibility(unittest.TestCase):

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

        issues = PanelSpecValidator().validate([spec])

        codes = {i.code for i in issues}

        self.assertIn(
            "PANEL_TOO_SMALL_FOR_MINIFIX",
            codes
        )
