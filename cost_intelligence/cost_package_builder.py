from cost_intelligence.cost_package_report import CostPackageReport
from cost_intelligence.hardware_bom_cost_builder import HardwareCostBuilder
from manufacturing.factory_release_package import FactoryReleasePackage


class CostPackageBuilder:
    """Summarise cost-relevant evidence from a ``FactoryReleasePackage``.

    Reuses ``HardwareCostBuilder`` (the existing cost component) for
    hardware pricing.  Material, machining, and assembly costs are
    **not** priced at this layer — they require
    ``ManufacturingProductionPackage`` context that is outside the
    scope of ``FactoryReleasePackage``.  Unknown costs are reported
    as warnings, never as invented values.
    """

    MATERIAL_UNPRICED = (
        "Material cost cannot be calculated from FactoryReleasePackage — "
        "requires ManufacturingProductionPackage context"
    )
    MACHINING_UNPRICED = (
        "Machining cost cannot be calculated from FactoryReleasePackage — "
        "requires ManufacturingProductionPackage context"
    )
    ASSEMBLY_UNPRICED = (
        "Assembly cost cannot be calculated from FactoryReleasePackage — "
        "requires ManufacturingProductionPackage context"
    )

    def __init__(self, pricing_catalog: dict | None = None):
        """*pricing_catalog* is optional; defaults to the standard catalog."""
        self._pricing_catalog = pricing_catalog

    # -- public API ---------------------------------------------------------

    def build(self, package: FactoryReleasePackage) -> CostPackageReport:
        warnings: list[str] = []
        hardware_cost = 0.0

        # -- hardware cost: delegate to existing cost component ------------
        hardware_cost, hw_warnings = self._calculate_hardware_cost(package)
        warnings.extend(hw_warnings)

        # -- material cost: count but warn not priced at this layer --------
        cut_list_items = self._count_items(package.cut_list, "items")
        if cut_list_items > 0:
            warnings.append(self.MATERIAL_UNPRICED)

        # -- machining cost: count but warn not priced at this layer -------
        cnc_rows = self._count_items(package.cnc_package, "rows")
        if cnc_rows > 0:
            warnings.append(self.MACHINING_UNPRICED)

        # -- assembly cost: count but warn not priced at this layer --------
        assembly_rows = self._count_items(package.assembly_package, "rows")
        if assembly_rows > 0:
            warnings.append(self.ASSEMBLY_UNPRICED)

        return CostPackageReport(
            material_cost_total=0.0,
            hardware_cost_total=hardware_cost,
            machining_cost_total=0.0,
            assembly_cost_total=0.0,
            total_cost=hardware_cost,
            warnings=warnings,
            source="CostPackageBuilder",
        )

    # -- internal helpers ---------------------------------------------------

    def _calculate_hardware_cost(self, package):
        """Return (total_cost, warnings) using the existing HardwareCostBuilder."""
        hardware_bom = package.hardware_bom
        if hardware_bom is None:
            return 0.0, []

        cost_report = HardwareCostBuilder().build(
            hardware_bom, pricing_catalog=self._pricing_catalog
        )
        return (
            getattr(cost_report, "total_hardware_cost", 0.0),
            list(getattr(cost_report, "warnings", [])),
        )

    @staticmethod
    def _count_items(obj, field_name):
        """Safely count items on an object via ``getattr``."""
        if obj is None:
            return 0
        items = getattr(obj, field_name, []) or []
        return len(items)
