from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow


class HardwareBomBuilder:

    def build(self, hardware_usage_report):
        report = HardwareBomReport()
        sku_counts = getattr(hardware_usage_report, "hardware_sku_counts", {}) or {}
        sku_metadata = getattr(hardware_usage_report, "hardware_sku_metadata", {}) or {}

        report.bom_rows = [
            self._row(sku, quantity, sku_metadata.get(sku, {}))
            for sku, quantity in sku_counts.items()
            if quantity and quantity > 0
        ]
        return report

    @staticmethod
    def _row(sku, quantity, metadata):
        return HardwareBomRow(
            bom_category="HARDWARE",
            sku=sku,
            description=str(metadata.get("description", "") or sku),
            quantity=quantity,
            unit=str(metadata.get("unit", "") or "pcs"),
            component_reference=tuple(
                metadata.get("component_reference", ()) or ()
            ),
            cabinet_reference=tuple(
                metadata.get("cabinet_reference", ()) or ()
            ),
            hardware_category=str(
                metadata.get("hardware_category", "") or ""
            ),
            source_operation_references=tuple(
                metadata.get("source_operation_references", ()) or ()
            ),
        )
