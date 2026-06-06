import inspect
import unittest

from manufacturing.unified_operation_collector import (
    UnifiedOperationCollector,
)

from manufacturing.hybrid_extractor import (
    HybridManufacturingExtractor,
)


class TestNoLegacyOperationTypesInCanonicalRuntime(
    unittest.TestCase
):

    def test_collect_canonical_has_no_legacy_types(self):

        source = inspect.getsource(
            UnifiedOperationCollector.collect_canonical
        )

        self.assertNotIn("FaceDrill", source)
        self.assertNotIn("EdgeDrill", source)
        self.assertNotIn("Groove", source)

    def test_hybrid_extractor_has_no_legacy_types(self):

        source = inspect.getsource(
            HybridManufacturingExtractor.extract
        )

        self.assertNotIn("FaceDrill", source)
        self.assertNotIn("EdgeDrill", source)
        self.assertNotIn("Groove", source)


if __name__ == "__main__":
    unittest.main()
