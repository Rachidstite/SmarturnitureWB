from manufacturing.manufacturing_edge_report import ManufacturingEdgeReport


class ManufacturingEdgeBuilder:

    def build(self, package):
        items = []

        for panel in package.panels:
            for edge, banding in panel.edge_spec.all_banded().items():
                dimension = (
                    panel.width
                    if edge in ("TOP", "BOTTOM")
                    else panel.height
                )
                items.append(
                    {
                        "panel_identity": panel.identity,
                        "edge": edge,
                        "banding": banding,
                        "linear_meters": dimension / 1000,
                    }
                )

        return ManufacturingEdgeReport(
            items=items,
            total_items=len(items),
            total_linear_meters=round(
                sum(item["linear_meters"] for item in items),
                3,
            ),
            warnings=package.warnings,
        )
