from manufacturing.cnc_report import CNCReport, CNCReportRow


class CNCReportBuilder:
    def build(self, machining_report):
        report = CNCReport()
        report.rows = [
            self._row(item)
            for item in getattr(machining_report, "items", []) or []
        ]
        report.warnings = list(getattr(machining_report, "warnings", []) or [])
        return report

    @staticmethod
    def _row(item):
        source_reference = str(
            item.get("source_operation_reference")
            or item.get("source_operation_id")
            or item.get("source")
            or ""
        ).strip()
        panel_identity = str(
            item.get("panel_identity")
            or item.get("panel_id")
            or source_reference
            or ""
        ).strip()

        return CNCReportRow(
            panel_identity=panel_identity,
            operation_type=str(item.get("operation_type", "") or ""),
            face=str(item.get("face", "") or ""),
            x=float(item.get("x", 0.0) or 0.0),
            y=float(item.get("y", 0.0) or 0.0),
            z=float(item.get("z", 0.0) or 0.0),
            diameter=float(item.get("diameter", 0.0) or 0.0),
            depth=float(item.get("depth", 0.0) or 0.0),
            axis=str(item.get("axis", "") or "Z"),
            is_through=bool(item.get("is_through", False)),
            source_operation_reference=source_reference,
        )
