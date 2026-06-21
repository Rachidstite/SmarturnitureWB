from manufacturing.manufacturing_complexity_report import (
    ManufacturingComplexityReport,
)


class ManufacturingComplexityBuilder:

    _ENGINEERING_MINUTES_BASE_BY_LEVEL = {
        "LOW": 10.0,
        "MEDIUM": 25.0,
        "HIGH": 45.0,
        "EXTREME": 70.0,
    }

    _ENGINEERING_MINUTES_MULTIPLIER_BY_LEVEL = {
        "LOW": 0.50,
        "MEDIUM": 0.75,
        "HIGH": 1.00,
        "EXTREME": 1.25,
    }

    def build(self, metrics_report, joinery_report=None):
        score = 0
        main_drivers = []
        recommendations = []

        if metrics_report.total_panels >= 50:
            score += 25
            main_drivers.append("High panel count")
        elif metrics_report.total_panels >= 20:
            score += 15
            main_drivers.append("Moderate panel count")
        else:
            score += 5

        if metrics_report.total_drilling_operations >= 200:
            score += 25
            main_drivers.append("High drilling complexity")
        elif metrics_report.total_drilling_operations >= 60:
            score += 15
            main_drivers.append("Moderate drilling complexity")
        else:
            score += 5

        if metrics_report.total_edge_meters >= 120:
            score += 25
            main_drivers.append("High edge banding workload")
        elif metrics_report.total_edge_meters >= 40:
            score += 15
            main_drivers.append("Moderate edge banding workload")
        else:
            score += 5

        if metrics_report.total_material_types >= 4:
            score += 25
            main_drivers.append("Multiple material types")
        elif metrics_report.total_material_types >= 2:
            score += 10
            main_drivers.append("Multiple material types")
        else:
            score += 0

        score = min(100, score)

        if score >= 70:
            complexity_level = "HIGH"
            recommendations.append(
                "Review production planning and scheduling before release."
            )
        elif score >= 40:
            complexity_level = "MEDIUM"
            recommendations.append(
                "Review manufacturing workload before production."
            )
        else:
            complexity_level = "LOW"

        if joinery_report is not None:
            engineering_score = (
                joinery_report.joinery_complexity_score
                + metrics_report.total_panels
            )
        else:
            engineering_score = (
                metrics_report.total_drilling_operations * 0.5
                + metrics_report.total_panels
            )

        if engineering_score >= 86:
            engineering_complexity = "EXTREME"
        elif engineering_score >= 61:
            engineering_complexity = "HIGH"
        elif engineering_score >= 31:
            engineering_complexity = "MEDIUM"
        else:
            engineering_complexity = "LOW"

        estimated_engineering_minutes = self._estimate_engineering_minutes(
            metrics_report,
            engineering_complexity,
            joinery_report=joinery_report,
        )

        return ManufacturingComplexityReport(
            complexity_level=complexity_level,
            complexity_score=score,
            engineering_complexity=engineering_complexity,
            estimated_engineering_minutes=estimated_engineering_minutes,
            main_drivers=main_drivers,
            recommendations=recommendations,
            warnings=list(metrics_report.warnings),
        )

    def _estimate_engineering_minutes(
        self,
        metrics_report,
        engineering_complexity,
        joinery_report=None,
    ):
        base_minutes = self._ENGINEERING_MINUTES_BASE_BY_LEVEL.get(
            engineering_complexity,
            self._ENGINEERING_MINUTES_BASE_BY_LEVEL["LOW"],
        )
        multiplier = self._ENGINEERING_MINUTES_MULTIPLIER_BY_LEVEL.get(
            engineering_complexity,
            self._ENGINEERING_MINUTES_MULTIPLIER_BY_LEVEL["LOW"],
        )

        if joinery_report is not None:
            joinery_complexity_score = float(
                getattr(joinery_report, "joinery_complexity_score", 0.0)
            )
            estimated_minutes = base_minutes + (
                joinery_complexity_score * multiplier
            )
        else:
            estimated_minutes = base_minutes + (
                float(metrics_report.total_panels) * 0.5
                + float(metrics_report.total_drilling_operations) * 0.25
            )

        return round(max(0.0, estimated_minutes), 2)
