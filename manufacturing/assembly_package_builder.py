from manufacturing.assembly_package_report import (
    AssemblyPanelInventoryRow,
    AssemblyPackageReport,
    AssemblyPackageRow,
)


class AssemblyPackageBuilder:
    def build(self, production_package):
        report = AssemblyPackageReport()
        hardware_rows = getattr(
            getattr(production_package, "hardware_report", None),
            "bom_rows",
            None,
        ) or []
        cnc_rows = list(
            getattr(getattr(production_package, "cnc_report", None), "rows", None)
            or []
        )
        warnings = list(getattr(production_package, "warnings", []) or [])
        report.rows = [
            self._row(hardware_row, cnc_rows)
            for hardware_row in hardware_rows
        ]
        report.warnings = warnings
        report.panel_inventory = self._panel_inventory_rows(
            getattr(production_package, "product_bom_report", None)
        )
        return report

    @staticmethod
    def _row(hardware_row, cnc_rows):
        source_operation_references = tuple(
            getattr(hardware_row, "source_operation_references", ()) or ()
        )
        related_cnc_rows = AssemblyPackageBuilder._match_cnc_rows(
            cnc_rows,
            source_operation_references,
        )
        notes = []
        description = str(getattr(hardware_row, "description", "") or "").strip()
        if description:
            notes.append(description)

        if not notes and getattr(hardware_row, "hardware_category", ""):
            notes.append(str(getattr(hardware_row, "hardware_category", "") or ""))

        return AssemblyPackageRow(
            cabinet_reference=tuple(
                getattr(hardware_row, "cabinet_reference", ()) or ()
            ),
            component_reference=tuple(
                getattr(hardware_row, "component_reference", ()) or ()
            ),
            assembly_group=str(
                getattr(hardware_row, "hardware_category", "") or ""
            ),
            hardware_required=str(getattr(hardware_row, "sku", "") or getattr(hardware_row, "hardware_sku", "") or ""),
            hardware_quantity=int(getattr(hardware_row, "quantity", 0) or 0),
            joinery_reference=source_operation_references,
            required_machining=tuple(related_cnc_rows),
            assembly_notes=tuple(notes),
            source_operation_references=source_operation_references,
        )

    @staticmethod
    def _match_cnc_rows(cnc_rows, source_operation_references):
        if not source_operation_references:
            return ()

        source_set = set(source_operation_references)
        return tuple(
            cnc_row
            for cnc_row in cnc_rows
            if str(
                getattr(cnc_row, "source_operation_reference", "") or ""
            ).strip()
            in source_set
        )

    @staticmethod
    def _panel_inventory_rows(product_bom_report):
        rows = getattr(product_bom_report, "rows", ()) or ()
        return tuple(
            AssemblyPanelInventoryRow(
                cabinet_reference=tuple(getattr(row, "cabinet_reference", ()) or ()),
                component_reference=tuple(
                    getattr(row, "component_reference", ()) or ()
                ),
                panel_identity=str(getattr(row, "identity", "") or ""),
                description=str(getattr(row, "description", "") or ""),
                quantity=int(getattr(row, "quantity", 0) or 0),
                unit=str(getattr(row, "unit", "") or ""),
                material=getattr(row, "material", None),
                width_mm=getattr(row, "width_mm", None),
                height_mm=getattr(row, "height_mm", None),
                thickness_mm=getattr(row, "thickness_mm", None),
                component_role=getattr(row, "component_role", None),
                group=getattr(row, "group", None),
            )
            for row in rows
            if str(getattr(row, "bom_category", "") or "") == "PANEL"
        )
