from cost_intelligence.hardware_bom_cost_report import (
    HardwareBomCostLineItem,
    HardwareBomCostReport,
)
from cost_intelligence.default_catalog_service import DefaultCatalogService


class HardwareCostBuilder:

    def build(self, hardware_bom_report, pricing_catalog=None):
        pricing_catalog = (
            pricing_catalog
            if pricing_catalog is not None
            else DefaultCatalogService().load_default_catalog()
        )
        report = HardwareBomCostReport()
        line_items = []
        warnings = []
        total_hardware_cost = 0.0

        for row in getattr(hardware_bom_report, "bom_rows", []) or []:
            sku = getattr(row, "hardware_sku", "")
            quantity = getattr(row, "quantity", 0)
            price = pricing_catalog.get(sku)

            if price is None:
                unit_cost = 0.0
                total_cost = 0.0
                warnings.append(f"Missing hardware price for {sku}")
            else:
                unit_cost = float(price.get("unit_price", 0.0))
                total_cost = quantity * unit_cost

            line_items.append(
                HardwareBomCostLineItem(
                    hardware_sku=sku,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    total_cost=total_cost,
                )
            )
            total_hardware_cost += total_cost

        report.line_items = line_items
        report.total_hardware_cost = total_hardware_cost
        report.warnings = warnings
        return report
