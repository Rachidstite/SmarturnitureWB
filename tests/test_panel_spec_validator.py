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
