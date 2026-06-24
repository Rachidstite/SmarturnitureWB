from manufacturing.factory_delivery_report import FactoryDeliveryReport


class FactoryDeliveryBuilder:

    def build(self, operational_report, schedule_report):
        if getattr(operational_report, "operational_status", "READY") == "BLOCKED":
            delivery_status = "DELAYED"
        elif (
            getattr(operational_report, "delivery_risk", "LOW") == "HIGH"
            or getattr(schedule_report, "schedule_risk_level", "LOW") == "HIGH"
        ):
            delivery_status = "AT_RISK"
        else:
            delivery_status = "ON_TRACK"

        if delivery_status == "ON_TRACK":
            delivery_confidence = "HIGH"
        elif delivery_status == "AT_RISK":
            delivery_confidence = "MEDIUM"
        else:
            delivery_confidence = "LOW"

        if delivery_status == "DELAYED":
            delivery_recommendation = "Delivery is delayed"
        elif delivery_status == "AT_RISK":
            delivery_recommendation = "Delivery review required"
        else:
            delivery_recommendation = ""

        return FactoryDeliveryReport(
            delivery_status=delivery_status,
            delivery_confidence=delivery_confidence,
            delivery_recommendation=delivery_recommendation,
        )
