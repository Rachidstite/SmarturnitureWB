from __future__ import annotations

from manufacturing.factory_release_package import FactoryReleasePackage


class FactoryReleaseExporter:
    """Read-only view/serializer for ``FactoryReleasePackage``.

    Produces a plain dict (or deterministic text) from the package.
    No external engine or pipeline dependency.
    Never modifies the package.
    """

    # -- public API ---------------------------------------------------------

    @staticmethod
    def export(package: FactoryReleasePackage) -> dict:
        """Return a plain dict summary of *package*.

        Counts are read via ``getattr`` — the exporter tolerates
        ``None`` sub-objects and missing attributes without raising.
        """
        decision = package.manufacturing_decision
        cut_list = package.cut_list
        hardware_bom = package.hardware_bom
        cnc_package = package.cnc_package
        assembly_package = package.assembly_package

        # -- decision fields ------------------------------------------------
        decision_status = ""
        ready_for_production = False
        warning_reasons: list[str] = []
        if decision is not None:
            decision_status = str(getattr(decision, "status", ""))
            ready_for_production = bool(
                getattr(decision, "ready_for_production", False)
            )
            raw = getattr(decision, "warning_reasons", ())
            warning_reasons = list(raw) if raw else []

        # -- item counts via duck-typing ------------------------------------
        cut_list_items = (
            getattr(cut_list, "items", []) if cut_list is not None else []
        )
        bom_rows = (
            getattr(hardware_bom, "bom_rows", []) if hardware_bom is not None else []
        )
        cnc_rows = (
            getattr(cnc_package, "rows", []) if cnc_package is not None else []
        )
        assembly_rows = (
            getattr(assembly_package, "rows", [])
            if assembly_package is not None
            else []
        )

        return {
            "manufacturing_decision_status": decision_status,
            "ready_for_production": ready_for_production,
            "warning_reasons": warning_reasons,
            "release_warnings": list(package.warnings),
            "cut_list_item_count": len(cut_list_items),
            "hardware_bom_row_count": len(bom_rows),
            "cnc_row_count": len(cnc_rows),
            "assembly_row_count": len(assembly_rows),
            "metadata": dict(package.metadata),
        }

    @staticmethod
    def render_text(package: FactoryReleasePackage) -> str:
        """Return a human-readable text summary of *package*.

        Deterministic — same input always produces the same output.
        """
        d = FactoryReleaseExporter.export(package)
        lines = [
            f"Manufacturing Decision Status : {d['manufacturing_decision_status']}",
            f"Ready For Production          : {d['ready_for_production']}",
            "",
            f"Cut List Items                : {d['cut_list_item_count']}",
            f"Hardware BOM Rows             : {d['hardware_bom_row_count']}",
            f"CNC Rows                      : {d['cnc_row_count']}",
            f"Assembly Rows                 : {d['assembly_row_count']}",
            "",
        ]
        rw = d["release_warnings"]
        if rw:
            lines.append(f"Release Warnings ({len(rw)}):")
            for w in rw:
                lines.append(f"  - {w}")
            lines.append("")
        wr = d["warning_reasons"]
        if wr:
            lines.append(f"Decision Warning Reasons ({len(wr)}):")
            for w in wr:
                lines.append(f"  - {w}")
            lines.append("")
        if d["metadata"]:
            lines.append(f"Metadata keys: {list(d['metadata'].keys())}")
        lines.append("--- end of factory release export ---")
        return "\n".join(lines)
