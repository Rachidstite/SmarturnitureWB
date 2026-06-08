import unittest

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)


class FakeOp:
    def __init__(self):
        self.metadata = {}


class FakePanel:
    def __init__(self):
        self.identity = "panel1"
        self.role = "SIDE"
        self.thickness = 18


class FakeGraph:
    physical_nodes = []


class TestRuntimePanelSpecPopulation(
    unittest.TestCase
):

    def test_extractor_returns_panel_specs(self):

        specs = (
            HybridManufacturingExtractor.extract(
                FakeGraph()
            )
        )

        self.assertIsNotNone(
            specs
        )


if __name__ == "__main__":
    unittest.main()
