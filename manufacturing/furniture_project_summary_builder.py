from manufacturing.furniture_project_summary import FurnitureProjectSummary


class FurnitureProjectSummaryBuilder:

    def build(self, furniture_project):
        physical_nodes = [
            node
            for cabinet in furniture_project.cabinets
            for node in cabinet.graph.physical_nodes
        ]

        return FurnitureProjectSummary(
            total_cabinets=len(furniture_project.cabinets),
            total_physical_parts=len(physical_nodes),
            total_machining_operations=sum(
                len(node.machining_ops)
                for node in physical_nodes
            ),
        )
