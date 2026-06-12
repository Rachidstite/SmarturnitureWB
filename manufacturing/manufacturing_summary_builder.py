from manufacturing.manufacturing_summary_report import ManufacturingSummaryReport


class ManufacturingSummaryBuilder:

    def build(self, package):
        return ManufacturingSummaryReport(
            total_panels=len(package.panels),
            total_materials=len(package.materials),
            total_edge_operations=len(package.edge_operations),
            total_machining_operations=len(package.machining_operations),
            warnings=package.warnings,
        )
