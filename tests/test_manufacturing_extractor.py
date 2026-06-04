import unittest

from domain.builders import WardrobeBuilder
from manufacturing.extractor import ManufacturingExtractor


class TestManufacturingExtractor(unittest.TestCase):

    def test_reference_dimensions(self):

        project = WardrobeBuilder(
            uid="EXTRACTOR_TEST",
            width=800,
            height=800,
            depth=400
        ).build()

        specs = ManufacturingExtractor.extract(
            project.graph
        )

        by_id = {
            s.identity: s
            for s in specs
        }

        self.assertEqual(
            by_id["EXTRACTOR_TEST_SIDE_L"].width,
            400
        )

        self.assertEqual(
            by_id["EXTRACTOR_TEST_SIDE_L"].height,
            800
        )

        self.assertEqual(
            by_id["EXTRACTOR_TEST_TOP"].width,
            764.0
        )

        self.assertEqual(
            by_id["EXTRACTOR_TEST_TOP"].height,
            400
        )

        self.assertEqual(
            by_id["EXTRACTOR_TEST_BACK"].width,
            782.0
        )

        self.assertEqual(
            by_id["EXTRACTOR_TEST_BACK"].height,
            782.0
        )


if __name__ == "__main__":
    unittest.main()
