from manufacturing.assembly_intelligence_report import (
    AssemblyIntelligenceReport,
)


class AssemblyIntelligenceBuilder:

    def build(self, joinery_intelligence_report):
        joinery_complexity_score = int(
            getattr(joinery_intelligence_report, "joinery_complexity_score", 0)
        )
        total_face_holes = int(
            getattr(joinery_intelligence_report, "total_face_holes", 0)
        )
        total_edge_holes = int(
            getattr(joinery_intelligence_report, "total_edge_holes", 0)
        )

        assembly_time_minutes = joinery_complexity_score * 2
        joinery_density = total_face_holes + total_edge_holes

        if joinery_complexity_score < 50:
            assembly_complexity = "LOW"
            required_installers = 1
        elif joinery_complexity_score <= 120:
            assembly_complexity = "MEDIUM"
            required_installers = 1
        else:
            assembly_complexity = "HIGH"
            required_installers = 2

        installation_risk = assembly_complexity

        warnings = list(getattr(joinery_intelligence_report, "warnings", []) or [])
        if joinery_density == 0:
            warnings.append("No assembly joinery detected")

        return AssemblyIntelligenceReport(
            assembly_time_minutes=assembly_time_minutes,
            assembly_complexity=assembly_complexity,
            required_installers=required_installers,
            joinery_density=joinery_density,
            installation_risk=installation_risk,
            warnings=warnings,
        )
