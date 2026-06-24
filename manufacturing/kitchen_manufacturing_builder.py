from manufacturing.kitchen_manufacturing_report import KitchenManufacturingReport


class KitchenManufacturingBuilder:

    def build(self, cabinet_count=0, drawer_count=0, door_count=0):
        total_units = cabinet_count + drawer_count + door_count

        if total_units >= 50:
            manufacturing_complexity = "HIGH"
            requires_engineering_review = True
            manufacturing_recommendation = "Kitchen manufacturing review required"
        elif total_units >= 20:
            manufacturing_complexity = "MEDIUM"
            requires_engineering_review = False
            manufacturing_recommendation = (
                "Kitchen manufacturing review recommended"
            )
        else:
            manufacturing_complexity = "LOW"
            requires_engineering_review = False
            manufacturing_recommendation = ""

        return KitchenManufacturingReport(
            cabinet_count=cabinet_count,
            drawer_count=drawer_count,
            door_count=door_count,
            manufacturing_complexity=manufacturing_complexity,
            requires_engineering_review=requires_engineering_review,
            manufacturing_recommendation=manufacturing_recommendation,
        )
