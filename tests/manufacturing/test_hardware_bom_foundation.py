import inspect
import unittest


class TestHardwareBomFoundation(unittest.TestCase):
    def test_door_hardware_appears_in_generic_bom(self):
        report = self._build_bom_report(
            [
                self._operation(
                    sku="HINGE_BLUM_110_V1",
                    family="HINGE",
                    intent="INTENT_HINGE",
                    description="Blum 110 degree hinge",
                    component_reference="door-01",
                    cabinet_reference="cabinet-01",
                ),
                self._operation(
                    sku="HINGE_BLUM_110_V1",
                    family="HINGE",
                    intent="INTENT_HINGE",
                    description="Blum 110 degree hinge",
                    component_reference="door-01",
                    cabinet_reference="cabinet-01",
                ),
            ]
        )

        self.assertEqual(len(report.bom_rows), 1)
        row = report.bom_rows[0]
        self.assertEqual(row.sku, "HINGE_BLUM_110_V1")
        self.assertEqual(row.hardware_sku, "HINGE_BLUM_110_V1")
        self.assertEqual(row.bom_category, "HARDWARE")
        self.assertEqual(row.description, "Blum 110 degree hinge")
        self.assertEqual(row.quantity, 2)
        self.assertEqual(row.unit, "pcs")
        self.assertEqual(row.component_reference, ("door-01",))
        self.assertEqual(row.cabinet_reference, ("cabinet-01",))
        self.assertEqual(row.hardware_category, "HINGE")
        self.assertEqual(row.source_operation_references, ())

    def test_drawer_hardware_appears_in_generic_bom(self):
        report = self._build_bom_report(
            [
                self._operation(
                    sku="DRAWER_SLIDE_STANDARD_450",
                    family="DRAWER_SLIDE",
                    intent="INTENT_DRAWER_SLIDE",
                    description="450mm standard drawer slide",
                    component_reference="drawer-01",
                    cabinet_reference="cabinet-01",
                ),
                self._operation(
                    sku="DRAWER_SLIDE_STANDARD_450",
                    family="DRAWER_SLIDE",
                    intent="INTENT_DRAWER_SLIDE",
                    description="450mm standard drawer slide",
                    component_reference="drawer-01",
                    cabinet_reference="cabinet-01",
                ),
            ]
        )

        self.assertEqual(len(report.bom_rows), 1)
        row = report.bom_rows[0]
        self.assertEqual(row.sku, "DRAWER_SLIDE_STANDARD_450")
        self.assertEqual(row.quantity, 2)
        self.assertEqual(row.component_reference, ("drawer-01",))
        self.assertEqual(row.hardware_category, "DRAWER_SLIDE")
        self.assertEqual(row.source_operation_references, ())

    def test_mixed_cabinet_aggregates_identical_sku_without_duplicate_rows(self):
        report = self._build_bom_report(
            [
                self._operation(
                    sku="HANDLE_128_BLACK",
                    family="HANDLE",
                    intent="INTENT_HANDLE",
                    component_reference="door-01",
                    cabinet_reference="cabinet-01",
                ),
                self._operation(
                    sku="HANDLE_128_BLACK",
                    family="HANDLE",
                    intent="INTENT_HANDLE",
                    component_reference="drawer-01",
                    cabinet_reference="cabinet-01",
                ),
            ]
        )

        self.assertEqual(
            [(row.sku, row.quantity) for row in report.bom_rows],
            [("HANDLE_128_BLACK", 2)],
        )
        self.assertEqual(
            report.bom_rows[0].component_reference,
            ("door-01", "drawer-01"),
        )
        self.assertEqual(report.bom_rows[0].source_operation_references, ())

    def test_different_sku_remain_separate(self):
        report = self._build_bom_report(
            [
                self._operation(
                    sku="HINGE_BLUM_110_V1",
                    family="HINGE",
                    intent="INTENT_HINGE",
                    component_reference="door-01",
                ),
                self._operation(
                    sku="DRAWER_SLIDE_STANDARD_450",
                    family="DRAWER_SLIDE",
                    intent="INTENT_DRAWER_SLIDE",
                    component_reference="drawer-01",
                ),
            ]
        )

        self.assertEqual(
            [(row.sku, row.quantity) for row in report.bom_rows],
            [
                ("HINGE_BLUM_110_V1", 1),
                ("DRAWER_SLIDE_STANDARD_450", 1),
            ],
        )

    def test_empty_cabinet_produces_empty_bom(self):
        report = self._build_bom_report([])

        self.assertEqual(report.bom_rows, [])
        self.assertEqual(report.warnings, [])

    def test_source_operation_references_are_preserved_when_present(self):
        report = self._build_bom_report(
            [
                self._operation(
                    sku="HINGE_BLUM_110_V1",
                    family="HINGE",
                    intent="INTENT_HINGE",
                    source_operation_reference="op-1",
                ),
                self._operation(
                    sku="HINGE_BLUM_110_V1",
                    family="HINGE",
                    intent="INTENT_HINGE",
                    source_operation_reference="op-2",
                ),
            ]
        )

        self.assertEqual(
            report.bom_rows[0].source_operation_references,
            ("op-1", "op-2"),
        )

    def test_generic_bom_uses_existing_usage_evidence_only(self):
        import manufacturing.hardware_bom_builder as bom_builder
        import manufacturing.hardware_usage_builder as usage_builder

        bom_source = inspect.getsource(bom_builder)
        usage_source = inspect.getsource(usage_builder)

        self.assertIn("hardware_sku_counts", bom_source)
        for token in (
            "HardwareBomEngine",
            "DoorHardwareBomBuilder",
            "DrawerHardwareBomBuilder",
            "GeometryEngine",
            "SceneGraph",
            "cost_intelligence",
            "Commercial",
        ):
            self.assertNotIn(token, bom_source)
            self.assertNotIn(token, usage_source)

    @staticmethod
    def _build_bom_report(operations):
        from manufacturing.hardware_bom_builder import HardwareBomBuilder
        from manufacturing.hardware_usage_builder import HardwareUsageBuilder
        from manufacturing.manufacturing_package import ManufacturingPackage

        usage_report = HardwareUsageBuilder().build(
            ManufacturingPackage(machining_operations=operations)
        )
        return HardwareBomBuilder().build(usage_report)

    @staticmethod
    def _operation(
        sku,
        family,
        intent,
        description="",
        component_reference="",
        cabinet_reference="",
        source_operation_reference="",
    ):
        from manufacturing.unified_manufacturing_operation import (
            UnifiedManufacturingOperation,
        )

        return UnifiedManufacturingOperation(
            operation_type="DRILL",
            metadata={
                "hardware_family": family,
                "hardware_sku": sku,
                "hardware_intent": intent,
                "hardware_description": description,
                "component_reference": component_reference,
                "cabinet_reference": cabinet_reference,
                "hardware_category": family,
                "hardware_unit": "pcs",
                "source_operation_reference": source_operation_reference,
            },
        )


if __name__ == "__main__":
    unittest.main()
