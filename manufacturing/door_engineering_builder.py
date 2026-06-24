from manufacturing.door_engineering_report import DoorEngineeringReport


HEIGHT_MEDIUM = 1200
HEIGHT_HIGH = 1800
WIDTH_MEDIUM = 500
WIDTH_HIGH = 600


class DoorEngineeringBuilder:

    def build(self, door_height=0.0, door_width=0.0):
        if door_height >= HEIGHT_HIGH:
            door_height_risk = "HIGH"
        elif door_height >= HEIGHT_MEDIUM:
            door_height_risk = "MEDIUM"
        else:
            door_height_risk = "LOW"

        if door_width >= WIDTH_HIGH:
            door_width_risk = "HIGH"
        elif door_width >= WIDTH_MEDIUM:
            door_width_risk = "MEDIUM"
        else:
            door_width_risk = "LOW"

        if door_height_risk == "HIGH" or door_width_risk == "HIGH":
            hinge_requirement = "HIGH"
            recommended_hinge_count = 4
            door_recommendation = "Door engineering review required"
        elif door_height_risk == "MEDIUM" or door_width_risk == "MEDIUM":
            hinge_requirement = "MEDIUM"
            recommended_hinge_count = 3
            door_recommendation = "Door engineering review recommended"
        else:
            hinge_requirement = "LOW"
            recommended_hinge_count = 2
            door_recommendation = ""

        return DoorEngineeringReport(
            door_height_risk=door_height_risk,
            door_width_risk=door_width_risk,
            hinge_requirement=hinge_requirement,
            recommended_hinge_count=recommended_hinge_count,
            door_recommendation=door_recommendation,
        )
