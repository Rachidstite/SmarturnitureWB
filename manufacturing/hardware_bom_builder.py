from manufacturing.hardware_bom_report import HardwareBomReport, HardwareBomRow


class HardwareBomBuilder:

    def build(self, hardware_usage_report):
        report = HardwareBomReport()
        sku_counts = getattr(hardware_usage_report, "hardware_sku_counts", {}) or {}

        report.bom_rows = [
            HardwareBomRow(hardware_sku=sku, quantity=quantity)
            for sku, quantity in sku_counts.items()
            if quantity and quantity > 0
        ]
        return report
