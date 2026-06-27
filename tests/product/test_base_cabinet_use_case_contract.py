import unittest
import re
from pathlib import Path


DOC_PATH = Path("docs/product/Cabinet_Manufacturing_Capability_V1.md")

REQUIRED_OBJECTS = (
    "Cabinet",
    "Side Panels",
    "Top Panel",
    "Bottom Panel",
    "Back Panel",
    "Two Doors",
    "One Internal Shelf",
    "Hinges",
    "Shelf Pins",
    "Edge Banding",
)

REQUIRED_OUTPUTS = (
    "3D Cabinet View",
    "Engineering Validation",
    "Manufacturing Validation",
    "BOM",
    "Cut List",
    "Hardware List",
    "Cost Summary",
    "Readiness Summary",
    "Quotation Draft",
)

ACCEPTANCE_CRITERIA = (
    "User can create the cabinet",
    "User can change width/height/depth",
    "Panels update consistently",
    "Doors remain aligned",
    "Shelf remains inside cabinet",
    "Back panel is represented",
    "Edge banding is represented",
    "Required hardware is represented",
    "Engineering validation can be run",
    "Manufacturing validation can be run",
    "Required outputs can be generated or are explicitly marked pending",
)

FORBIDDEN_TERMS = (
    "Factory Runtime",
    "Scheduler",
    "Machine Model",
    "SaaS",
    "AI",
    "Agent",
)


class TestBaseCabinetUseCaseContract(unittest.TestCase):
    def setUp(self):
        self.text = DOC_PATH.read_text(encoding="utf-8")

    def test_product_document_exists(self):
        self.assertTrue(DOC_PATH.exists(), f"Missing document: {DOC_PATH}")

    def test_mentions_official_use_case_name(self):
        self.assertIn("Design Base Cabinet with Two Doors and One Internal Shelf", self.text)

    def test_documents_all_required_objects(self):
        for item in REQUIRED_OBJECTS:
            with self.subTest(item=item):
                self.assertIn(item, self.text)

    def test_documents_all_required_outputs(self):
        for item in REQUIRED_OUTPUTS:
            with self.subTest(item=item):
                self.assertIn(item, self.text)

    def test_documents_acceptance_criteria(self):
        for item in ACCEPTANCE_CRITERIA:
            with self.subTest(item=item):
                self.assertIn(item, self.text)

    def test_does_not_mention_forbidden_v1_scope_terms(self):
        for term in FORBIDDEN_TERMS:
            with self.subTest(term=term):
                pattern = rf"\b{re.escape(term)}\b"
                self.assertIsNone(re.search(pattern, self.text, flags=re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
