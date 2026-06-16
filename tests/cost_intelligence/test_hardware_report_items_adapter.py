import copy
import unittest
from types import SimpleNamespace


class TestHardwareReportItemsAdapter(unittest.TestCase):

    def test_adapter_exists(self):
        from cost_intelligence.hardware_report_items_adapter import (
            HardwareReportItemsAdapter,
        )

        self.assertTrue(callable(HardwareReportItemsAdapter.from_report))

    def test_converts_minifix_to_minifix_sku(self):
        result = self._adapt({"MINIFIX": 8})

        self.assertEqual(
            result,
            [{"sku": "MINIFIX_15_V1", "quantity": 8}],
        )

    def test_converts_hinge_to_hinge_sku(self):
        result = self._adapt({"HINGE": 4})

        self.assertEqual(
            result,
            [{"sku": "HINGE_BLUM_110_V1", "quantity": 4}],
        )

    def test_converts_confirmat_to_confirmat_sku(self):
        result = self._adapt({"CONFIRMAT": 6})

        self.assertEqual(
            result,
            [{"sku": "CONFIRMAT_50_V1", "quantity": 6}],
        )

    def test_converts_shelf_pin_to_shelf_pin_sku(self):
        result = self._adapt({"SHELF_PIN": 8})

        self.assertEqual(
            result,
            [{"sku": "SHELF_PIN_5MM", "quantity": 8}],
        )

    def test_converts_drawer_slide_to_drawer_slide_sku(self):
        result = self._adapt({"DRAWER_SLIDE": 6})

        self.assertEqual(
            result,
            [{"sku": "DRAWER_SLIDE_SOFTCLOSE_450", "quantity": 6}],
        )

    def test_ignores_dowel(self):
        result = self._adapt({"DOWEL": 12})

        self.assertEqual(result, [])

    def test_ignores_zero_and_missing_quantities(self):
        result = self._adapt({"MINIFIX": 0})

        self.assertEqual(result, [])

    def test_returns_empty_list_for_empty_or_missing_hardware_items(self):
        from cost_intelligence.hardware_report_items_adapter import (
            HardwareReportItemsAdapter,
        )

        self.assertEqual(
            HardwareReportItemsAdapter.from_report(
                SimpleNamespace(hardware_items={})
            ),
            [],
        )
        self.assertEqual(
            HardwareReportItemsAdapter.from_report(SimpleNamespace()),
            [],
        )

    def test_does_not_mutate_input_report(self):
        from cost_intelligence.hardware_report_items_adapter import (
            HardwareReportItemsAdapter,
        )

        report = SimpleNamespace(
            hardware_items={
                "MINIFIX": 8,
                "DOWEL": 12,
                "HINGE": 4,
            }
        )
        original_hardware_items = copy.deepcopy(report.hardware_items)

        HardwareReportItemsAdapter.from_report(report)

        self.assertEqual(report.hardware_items, original_hardware_items)

    def test_preserves_minifix_then_hinge_output_order(self):
        result = self._adapt(
            {
                "HINGE": 4,
                "DOWEL": 12,
                "MINIFIX": 8,
            }
        )

        self.assertEqual(
            result,
            [
                {"sku": "MINIFIX_15_V1", "quantity": 8},
                {"sku": "HINGE_BLUM_110_V1", "quantity": 4},
            ],
        )

    def test_preserves_extended_output_order(self):
        result = self._adapt(
            {
                "SHELF_PIN": 8,
                "CONFIRMAT": 6,
                "HINGE": 4,
                "MINIFIX": 8,
                "DRAWER_SLIDE": 10,
            }
        )

        self.assertEqual(
            result,
            [
                {"sku": "MINIFIX_15_V1", "quantity": 8},
                {"sku": "HINGE_BLUM_110_V1", "quantity": 4},
                {"sku": "CONFIRMAT_50_V1", "quantity": 6},
                {"sku": "SHELF_PIN_5MM", "quantity": 8},
                {"sku": "DRAWER_SLIDE_SOFTCLOSE_450", "quantity": 10},
            ],
        )

    @staticmethod
    def _adapt(hardware_items):
        from cost_intelligence.hardware_report_items_adapter import (
            HardwareReportItemsAdapter,
        )

        return HardwareReportItemsAdapter.from_report(
            SimpleNamespace(hardware_items=hardware_items)
        )


if __name__ == "__main__":
    unittest.main()
