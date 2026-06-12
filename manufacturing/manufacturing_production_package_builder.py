from manufacturing.manufacturing_cutlist_builder import ManufacturingCutlistBuilder
from manufacturing.manufacturing_edge_builder import ManufacturingEdgeBuilder
from manufacturing.manufacturing_machining_builder import (
    ManufacturingMachiningBuilder,
)
from manufacturing.manufacturing_production_package import (
    ManufacturingProductionPackage,
)
from manufacturing.manufacturing_release_validator import (
    ManufacturingReleaseValidator,
)
from manufacturing.manufacturing_summary_builder import ManufacturingSummaryBuilder


class ManufacturingProductionPackageBuilder:

    def build(self, package):
        cutlist_report = ManufacturingCutlistBuilder().build(package)
        edge_report = ManufacturingEdgeBuilder().build(package)
        machining_report = ManufacturingMachiningBuilder().build(package)
        summary_report = ManufacturingSummaryBuilder().build(package)
        release_result = ManufacturingReleaseValidator().validate(package)

        return ManufacturingProductionPackage(
            cutlist_report=cutlist_report,
            edge_report=edge_report,
            machining_report=machining_report,
            summary_report=summary_report,
            release_ready=release_result["ready"],
            warnings=release_result["warnings"],
        )
