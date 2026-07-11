from manufacturing.manufacturing_cutlist_builder import ManufacturingCutlistBuilder
from manufacturing.assembly_package_builder import AssemblyPackageBuilder
from manufacturing.cnc_report_builder import CNCReportBuilder
from manufacturing.manufacturing_edge_builder import ManufacturingEdgeBuilder
from manufacturing.manufacturing_machining_builder import (
    ManufacturingMachiningBuilder,
)
from manufacturing.hardware_bom_builder import HardwareBomBuilder
from manufacturing.hardware_usage_builder import HardwareUsageBuilder
from manufacturing.manufacturing_production_package import (
    ManufacturingProductionPackage,
)
from manufacturing.product_bom_report import ProductBomReport, ProductBomRow
from manufacturing.manufacturing_release_validator import (
    ManufacturingReleaseValidator,
)
from manufacturing.manufacturing_summary_builder import ManufacturingSummaryBuilder


class ManufacturingProductionPackageBuilder:
    DOOR_HINGE_WARNING = "Door panels present but hinge hardware evidence is missing."

    def build(self, package):
        cutlist_report = ManufacturingCutlistBuilder().build(package)
        edge_report = ManufacturingEdgeBuilder().build(package)
        machining_report = ManufacturingMachiningBuilder().build(package)
        summary_report = ManufacturingSummaryBuilder().build(package)
        release_result = ManufacturingReleaseValidator().validate(package)
        hardware_usage_report = HardwareUsageBuilder().build(package)
        hardware_report = HardwareBomBuilder().build(hardware_usage_report)
        product_bom_report = self._build_product_bom_report(
            cutlist_report,
            hardware_report,
            getattr(package, "panels", []) or [],
        )
        cnc_report = CNCReportBuilder().build(machining_report)
        assembly_report = AssemblyPackageBuilder().build(
            ManufacturingProductionPackage(
                hardware_report=hardware_report,
                cnc_report=cnc_report,
                warnings=list(release_result["warnings"]),
            )
        )
        warnings = list(release_result["warnings"])

        if self._has_door_panels(package, cutlist_report) and not self._has_hinge_evidence(
            hardware_usage_report,
            hardware_report,
        ):
            warnings.append(self.DOOR_HINGE_WARNING)

        return ManufacturingProductionPackage(
            cutlist_report=cutlist_report,
            edge_report=edge_report,
            machining_report=machining_report,
            summary_report=summary_report,
            release_ready=release_result["ready"],
            warnings=warnings,
            product_bom_report=product_bom_report,
            cnc_report=cnc_report,
            assembly_report=assembly_report,
            hardware_report=hardware_report,
        )

    @staticmethod
    def _has_door_panels(package, cutlist_report):
        for panel in getattr(package, "panels", []) or []:
            role = getattr(panel, "role", "")
            role_name = getattr(role, "name", str(role))
            if role_name == "DOOR_PANEL":
                return True

        for item in getattr(cutlist_report, "items", []) or []:
            identity = str(item.get("identity", "") if isinstance(item, dict) else "")
            if "_DOOR-" in identity or identity.upper().startswith("DOOR"):
                return True

        return False

    @staticmethod
    def _has_hinge_evidence(hardware_usage_report, hardware_report):
        intent_counts = getattr(hardware_usage_report, "hardware_intent_counts", {}) or {}
        if intent_counts.get("INTENT_HINGE"):
            return True

        for row in getattr(hardware_report, "bom_rows", []) or []:
            sku = str(getattr(row, "hardware_sku", "") or "").upper()
            if "HINGE" in sku and getattr(row, "quantity", 0) > 0:
                return True

        return False

    @staticmethod
    def _build_product_bom_report(cutlist_report, hardware_report, panels):
        panels_by_identity = {
            str(getattr(panel, "identity", "") or ""): panel
            for panel in panels
        }
        rows = []

        for item in getattr(cutlist_report, "items", []) or []:
            identity = str(item.get("identity", "") or "")
            panel = panels_by_identity.get(identity)
            role_name = ManufacturingProductionPackageBuilder._panel_role_name(panel)
            group = str(getattr(panel, "group", "") or "").strip() or None
            rows.append(
                ProductBomRow(
                    bom_category="PANEL",
                    identity=identity,
                    description=role_name or identity,
                    quantity=int(item.get("quantity", 0) or 0),
                    unit="pcs",
                    component_reference=((identity,) if identity else ()),
                    cabinet_reference=(),
                    source_reference=((identity,) if identity else ()),
                    material=str(item.get("material", "") or "") or None,
                    width_mm=float(item["width"]) if item.get("width") is not None else None,
                    height_mm=float(item["height"]) if item.get("height") is not None else None,
                    thickness_mm=(
                        float(item["thickness"])
                        if item.get("thickness") is not None
                        else None
                    ),
                    component_role=role_name or None,
                    group=group,
                )
            )

        for row in getattr(hardware_report, "bom_rows", []) or []:
            rows.append(
                ProductBomRow(
                    bom_category=str(getattr(row, "bom_category", "") or "HARDWARE"),
                    identity=str(getattr(row, "hardware_sku", "") or ""),
                    description=str(getattr(row, "description", "") or ""),
                    quantity=int(getattr(row, "quantity", 0) or 0),
                    unit=str(getattr(row, "unit", "") or ""),
                    component_reference=tuple(
                        getattr(row, "component_reference", ()) or ()
                    ),
                    cabinet_reference=tuple(
                        getattr(row, "cabinet_reference", ()) or ()
                    ),
                    source_reference=tuple(
                        getattr(row, "source_operation_references", ()) or ()
                    ),
                )
            )

        warnings = []
        for source in (
            getattr(cutlist_report, "warnings", None),
            getattr(hardware_report, "warnings", None),
        ):
            for warning in list(source or []):
                if warning not in warnings:
                    warnings.append(warning)

        return ProductBomReport(
            rows=tuple(rows),
            warnings=tuple(warnings),
            source="ManufacturingProductionPackageBuilder",
        )

    @staticmethod
    def _panel_role_name(panel):
        role = getattr(panel, "role", None)
        if role is None:
            return ""
        return str(getattr(role, "name", role) or "").strip()
