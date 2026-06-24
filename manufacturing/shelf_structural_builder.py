from manufacturing.shelf_structural_report import ShelfStructuralReport


WIDTH_MEDIUM = 800.0
WIDTH_HIGH = 1000.0


class ShelfStructuralBuilder:

    def build(self, shelf_width=0.0, shelf_thickness=18.0):
        if shelf_width >= WIDTH_HIGH:
            span_risk = "HIGH"
        elif shelf_width >= WIDTH_MEDIUM:
            span_risk = "MEDIUM"
        else:
            span_risk = "LOW"

        if shelf_width >= WIDTH_HIGH and shelf_thickness <= 18:
            sagging_risk = "HIGH"
        else:
            sagging_risk = "LOW"

        support_required = span_risk == "HIGH"

        if span_risk == "HIGH":
            shelf_recommendation = "Shelf support recommended"
        elif span_risk == "MEDIUM":
            shelf_recommendation = "Shelf span should be reviewed"
        else:
            shelf_recommendation = ""

        return ShelfStructuralReport(
            span_risk=span_risk,
            sagging_risk=sagging_risk,
            support_required=support_required,
            shelf_recommendation=shelf_recommendation,
        )
