from manufacturing.factory_load_report import FactoryLoadReport


class FactoryLoadBuilder:

    def build(self, factory_resource_report, manufacturing_duration_report):
        weekly_capacity_minutes = (
            factory_resource_report.weekly_capacity_hours * 60.0
        )

        if weekly_capacity_minutes > 0:
            cnc_load_percent = (
                manufacturing_duration_report.estimated_cnc_minutes
                / weekly_capacity_minutes
                * 100.0
            )
            assembly_load_percent = (
                manufacturing_duration_report.estimated_assembly_minutes
                / weekly_capacity_minutes
                * 100.0
            )
            edge_banding_load_percent = (
                manufacturing_duration_report.estimated_edge_banding_minutes
                / weekly_capacity_minutes
                * 100.0
            )
        else:
            cnc_load_percent = 0.0
            assembly_load_percent = 0.0
            edge_banding_load_percent = 0.0

        loads = {
            "CNC": cnc_load_percent,
            "ASSEMBLY": assembly_load_percent,
            "EDGE_BANDING": edge_banding_load_percent,
        }
        bottleneck = max(loads, key=loads.get)
        highest_load = loads[bottleneck]

        if highest_load < 50:
            status = "LOW"
        elif highest_load <= 85:
            status = "MEDIUM"
        else:
            status = "HIGH"

        return FactoryLoadReport(
            cnc_load_percent=cnc_load_percent,
            assembly_load_percent=assembly_load_percent,
            edge_banding_load_percent=edge_banding_load_percent,
            bottleneck=bottleneck,
            status=status,
        )
