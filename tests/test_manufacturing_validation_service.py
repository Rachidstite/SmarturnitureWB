import unittest

from domain.builders import WardrobeBuilder
from services.manufacturing_validation_service import (
    ManufacturingValidationService
)


class TestManufacturingValidationService(unittest.TestCase):

    def test_valid_reference_project(self):

        project = WardrobeBuilder(
            uid="VALIDATION",
            width=800,
            height=800,
            depth=400
        ).build()

        state = ManufacturingValidationService.validate(
            project.graph
        )

        self.assertFalse(
            state.has_errors
        )


    def test_invalid_project_reports_width_error(self):

        project = WardrobeBuilder(
            uid="INVALID_WIDTH",
            width=0,
            height=800,
            depth=400
        ).build()

        state = ManufacturingValidationService.validate(
            project.graph
        )

        codes = {i.code for i in state.issues}

        self.assertTrue(
            state.has_errors
        )

        self.assertIn(
            "WIDTH_INVALID",
            codes
        )


if __name__ == "__main__":
    unittest.main()
