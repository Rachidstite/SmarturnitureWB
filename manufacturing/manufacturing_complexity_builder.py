from manufacturing.manufacturing_complexity_report import (
    ManufacturingComplexityReport,
)


class ManufacturingComplexityBuilder:

    def build(self, metrics_report):
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

        return ManufacturingComplexityReport(
            complexity_level=complexity_level,
            complexity_score=score,
            main_drivers=main_drivers,
            recommendations=recommendations,
            warnings=list(metrics_report.warnings),
        )
