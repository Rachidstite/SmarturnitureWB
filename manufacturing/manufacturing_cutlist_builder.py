from manufacturing.manufacturing_cutlist_report import ManufacturingCutlistReport


class ManufacturingCutlistBuilder:

    def build(self, package):
        items = [
            {
                "identity": panel.identity,
                "width": panel.width,
                "height": panel.height,
                "thickness": panel.thickness,
                "material": panel.material,
                "quantity": panel.quantity,
            }
            for panel in package.panels
        ]

        return ManufacturingCutlistReport(
            items=items,
            total_items=len(items),
            warnings=package.warnings,
        )
