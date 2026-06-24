from manufacturing.manufacturing_model_report import ManufacturingModelReport


class ManufacturingModelBuilder:

    def build(
        self,
        manufacturing_package=None,
        manufacturing_summary_report=None,
        manufacturing_metrics_report=None,
        manufacturing_duration_report=None,
        hardware_usage_report=None,
        hardware_bom_report=None,
        joinery_intelligence_report=None,
        manufacturing_simulation_report=None,
        inventory_counts=None,
        project_name="",
    ):
        panel_count = self._first_int(
            getattr(manufacturing_summary_report, "total_panels", None),
            len(getattr(manufacturing_package, "panels", []) or []),
            0,
        )
        total_sheet_count = self._first_int(
            getattr(manufacturing_summary_report, "total_materials", None),
            len(getattr(manufacturing_package, "materials", []) or []),
            0,
        )
        total_physical_parts = panel_count

        total_machining_operations = self._first_int(
            getattr(manufacturing_summary_report, "total_machining_operations", None),
            len(getattr(manufacturing_package, "machining_operations", []) or []),
            0,
        )
        total_drilling_operations = self._first_int(
            getattr(manufacturing_metrics_report, "total_drilling_operations", None),
            getattr(manufacturing_simulation_report, "drilling_operation_count", None),
            0,
        )
        total_edge_operations = self._first_int(
            getattr(manufacturing_summary_report, "total_edge_operations", None),
            len(getattr(manufacturing_package, "edge_operations", []) or []),
            0,
        )
        total_assembly_operations = self._first_int(
            getattr(manufacturing_simulation_report, "assembly_operation_count", None),
            panel_count,
            0,
        )

        total_minifix = self._first_int(
            getattr(joinery_intelligence_report, "total_minifix", None),
            self._intent_count(hardware_usage_report, "INTENT_MINIFIX"),
            0,
        )
        total_confirmats = self._first_int(
            self._intent_count(hardware_usage_report, "INTENT_CONFIRMAT"),
            0,
        )
        total_hinges = self._first_int(
            getattr(joinery_intelligence_report, "total_hinges", None),
            self._intent_count(hardware_usage_report, "INTENT_HINGE"),
            0,
        )
        total_drawer_slides = self._first_int(
            getattr(joinery_intelligence_report, "total_drawer_slides", None),
            self._intent_count(hardware_usage_report, "INTENT_DRAWER_SLIDE"),
            0,
        )
        total_handles = self._first_int(
            getattr(joinery_intelligence_report, "total_handles", None),
            self._intent_count(hardware_usage_report, "INTENT_HANDLE"),
            0,
        )

        hardware_sku_counts = self._copy_mapping(
            getattr(hardware_usage_report, "hardware_sku_counts", None)
        )
        hardware_family_counts = self._copy_mapping(
            getattr(hardware_usage_report, "hardware_family_counts", None)
        )
        hardware_intent_counts = self._copy_mapping(
            getattr(hardware_usage_report, "hardware_intent_counts", None)
        )
        bom_rows = self._copy_sequence(getattr(hardware_bom_report, "bom_rows", None))

        total_panel_area_m2 = self._first_float(
            getattr(manufacturing_metrics_report, "total_panel_area_m2", None),
            0.0,
        )
        total_edge_meters = self._first_float(
            getattr(manufacturing_metrics_report, "total_edge_meters", None),
            0.0,
        )
        sheet_utilization_percent = 0.0
        machining_operations_by_type = self._copy_mapping(
            getattr(manufacturing_metrics_report, "machining_operations_by_type", None)
        )

        estimated_cnc_minutes = self._first_float(
            getattr(manufacturing_duration_report, "estimated_cnc_minutes", None),
            getattr(manufacturing_simulation_report, "estimated_cnc_minutes", None),
            0.0,
        )
        estimated_drilling_minutes = self._first_float(
            getattr(manufacturing_duration_report, "estimated_drilling_minutes", None),
            getattr(manufacturing_simulation_report, "estimated_drilling_minutes", None),
            0.0,
        )
        estimated_edge_banding_minutes = self._first_float(
            getattr(
                manufacturing_duration_report,
                "estimated_edge_banding_minutes",
                None,
            ),
            getattr(
                manufacturing_simulation_report,
                "estimated_edge_banding_minutes",
                None,
            ),
            0.0,
        )
        estimated_assembly_minutes = self._first_float(
            getattr(manufacturing_duration_report, "estimated_assembly_minutes", None),
            getattr(manufacturing_simulation_report, "estimated_assembly_minutes", None),
            0.0,
        )
        total_production_minutes = self._first_float(
            getattr(manufacturing_duration_report, "total_production_minutes", None),
            getattr(
                manufacturing_simulation_report,
                "estimated_total_factory_minutes",
                None,
            ),
            0.0,
        )

        warnings = self._combine_unique_lists(
            getattr(manufacturing_package, "warnings", None),
            getattr(manufacturing_summary_report, "warnings", None),
            getattr(manufacturing_metrics_report, "warnings", None),
            getattr(manufacturing_duration_report, "warnings", None),
            getattr(hardware_bom_report, "warnings", None),
            getattr(joinery_intelligence_report, "warnings", None),
            getattr(manufacturing_simulation_report, "warnings", None),
        )

        recommendations = self._combine_recommendations(
            manufacturing_summary_report,
            manufacturing_metrics_report,
            manufacturing_duration_report,
            hardware_usage_report,
            hardware_bom_report,
            joinery_intelligence_report,
            manufacturing_simulation_report,
        )

        manufacturing_status = self._resolve_manufacturing_status(
            manufacturing_package=manufacturing_package,
            manufacturing_summary_report=manufacturing_summary_report,
            manufacturing_metrics_report=manufacturing_metrics_report,
            manufacturing_duration_report=manufacturing_duration_report,
            hardware_usage_report=hardware_usage_report,
            hardware_bom_report=hardware_bom_report,
            joinery_intelligence_report=joinery_intelligence_report,
            manufacturing_simulation_report=manufacturing_simulation_report,
            warnings=warnings,
        )

        return ManufacturingModelReport(
            project_name=project_name,
            cabinet_count=(
                inventory_counts.cabinet_count if inventory_counts is not None else 0
            ),
            panel_count=panel_count,
            drawer_count=0,
            door_count=(
                inventory_counts.door_count if inventory_counts is not None else 0
            ),
            shelf_count=(
                inventory_counts.shelf_count if inventory_counts is not None else 0
            ),
            back_panel_count=(
                inventory_counts.back_panel_count if inventory_counts is not None else 0
            ),
            total_physical_parts=total_physical_parts,
            total_sheet_count=total_sheet_count,
            total_machining_operations=total_machining_operations,
            total_drilling_operations=total_drilling_operations,
            total_edge_operations=total_edge_operations,
            total_assembly_operations=total_assembly_operations,
            total_minifix=total_minifix,
            total_confirmats=total_confirmats,
            total_hinges=total_hinges,
            total_drawer_slides=total_drawer_slides,
            total_handles=total_handles,
            hardware_sku_counts=hardware_sku_counts,
            hardware_family_counts=hardware_family_counts,
            hardware_intent_counts=hardware_intent_counts,
            bom_rows=bom_rows,
            total_panel_area_m2=total_panel_area_m2,
            total_edge_meters=total_edge_meters,
            sheet_utilization_percent=sheet_utilization_percent,
            machining_operations_by_type=machining_operations_by_type,
            estimated_cnc_minutes=estimated_cnc_minutes,
            estimated_drilling_minutes=estimated_drilling_minutes,
            estimated_edge_banding_minutes=estimated_edge_banding_minutes,
            estimated_assembly_minutes=estimated_assembly_minutes,
            total_production_minutes=total_production_minutes,
            manufacturing_status=manufacturing_status,
            warnings=warnings,
            blocking_issues=[],
            recommendations=recommendations,
        )

    @staticmethod
    def _first_int(*values):
        for value in values:
            if value is not None:
                return int(value)
        return 0

    @staticmethod
    def _first_float(*values):
        for value in values:
            if value is not None:
                return float(value)
        return 0.0

    @staticmethod
    def _copy_mapping(value):
        return dict(value) if value else {}

    @staticmethod
    def _copy_sequence(value):
        return list(value) if value else []

    @staticmethod
    def _intent_count(hardware_usage_report, intent_key):
        if hardware_usage_report is None:
            return None
        intent_counts = getattr(hardware_usage_report, "hardware_intent_counts", None) or {}
        count = intent_counts.get(intent_key)
        return int(count) if count is not None else None

    @staticmethod
    def _combine_unique_lists(*lists):
        combined = []
        seen = set()
        for source in lists:
            for item in list(source or []):
                if item not in seen:
                    seen.add(item)
                    combined.append(item)
        return combined

    @staticmethod
    def _combine_recommendations(
        manufacturing_summary_report,
        manufacturing_metrics_report,
        manufacturing_duration_report,
        hardware_usage_report,
        hardware_bom_report,
        joinery_intelligence_report,
        manufacturing_simulation_report,
    ):
        recommendations = []
        for report in (
            manufacturing_summary_report,
            manufacturing_metrics_report,
            manufacturing_duration_report,
            hardware_usage_report,
            hardware_bom_report,
            joinery_intelligence_report,
            manufacturing_simulation_report,
        ):
            for attr in (
                "recommendations",
                "recommendation",
                "recommended_action",
                "recommended_fix",
                "simulation_recommendation",
                "manufacturing_recommendation",
            ):
                value = getattr(report, attr, None)
                if value:
                    if isinstance(value, list):
                        recommendations.extend(value)
                    else:
                        recommendations.append(value)
        return recommendations

    @staticmethod
    def _resolve_manufacturing_status(
        manufacturing_package,
        manufacturing_summary_report,
        manufacturing_metrics_report,
        manufacturing_duration_report,
        hardware_usage_report,
        hardware_bom_report,
        joinery_intelligence_report,
        manufacturing_simulation_report,
        warnings,
    ):
        sources_present = any(
            report is not None
            for report in (
                manufacturing_package,
                manufacturing_summary_report,
                manufacturing_metrics_report,
                manufacturing_duration_report,
                hardware_usage_report,
                hardware_bom_report,
                joinery_intelligence_report,
                manufacturing_simulation_report,
            )
        )
        if not sources_present:
            return "UNKNOWN"
        return "REVIEW" if warnings else "READY"
