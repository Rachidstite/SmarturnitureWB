import unittest
from types import SimpleNamespace


class TestFactoryOperationsEndToEndContract(unittest.TestCase):

    def test_factory_operations_risk_chain_propagates_end_to_end(self):
        from manufacturing.factory_executive_decision_builder import (
            FactoryExecutiveDecisionBuilder,
        )
        from manufacturing.factory_capacity_intelligence_builder import (
            FactoryCapacityIntelligenceBuilder,
        )
        from manufacturing.factory_capacity_simulation_builder import (
            FactoryCapacitySimulationBuilder,
        )
        from manufacturing.factory_executive_intelligence_builder import (
            FactoryExecutiveIntelligenceBuilder,
        )
        from manufacturing.factory_resource_report import FactoryResourceReport
        from manufacturing.factory_operational_builder import (
            FactoryOperationalBuilder,
        )
        from manufacturing.manufacturing_duration_report import (
            ManufacturingDurationReport,
        )
        from manufacturing.manufacturing_simulation_builder import (
            ManufacturingSimulationBuilder,
        )
        from manufacturing.production_forecast_builder import (
            ProductionForecastBuilder,
        )
        from manufacturing.project_manufacturing_readiness_builder import (
            ProjectManufacturingReadinessBuilder,
        )

        manufacturing_package = self._manufacturing_package()
        structural_report = self._structural_report(structural_risk="HIGH")
        stability_report = self._stability_report()
        hardware_report = self._hardware_report()
        kitchen_report = self._kitchen_report()
        profitability_report = self._profitability_report()
        delivery_report = self._delivery_report(delivery_status="DELAYED")
        schedule_report = self._schedule_report(schedule_risk_level="HIGH")
        load_report = self._load_report(status="HIGH", bottleneck="CNC")
        bottleneck_report = self._bottleneck_report(
            bottleneck="CNC",
            severity="HIGH",
            recommendation="Increase CNC availability",
        )
        delivery_intelligence_report = self._delivery_intelligence_report()

        snapshots = [
            self._snapshot(manufacturing_package),
            self._snapshot(structural_report),
            self._snapshot(stability_report),
            self._snapshot(hardware_report),
            self._snapshot(kitchen_report),
            self._snapshot(profitability_report),
            self._snapshot(delivery_report),
            self._snapshot(schedule_report),
            self._snapshot(load_report),
            self._snapshot(bottleneck_report),
            self._snapshot(delivery_intelligence_report),
        ]

        simulation_report = ManufacturingSimulationBuilder().build(
            manufacturing_package
        )
        capacity_simulation_report = (
            FactoryCapacitySimulationBuilder().build(
                simulation_report,
                available_factory_minutes=5.0,
            )
        )
        forecast_report = ProductionForecastBuilder().build(
            simulation_report,
            available_factory_minutes_per_day=0.5,
        )
        readiness_report = ProjectManufacturingReadinessBuilder().build(
            cabinet_structural_report=structural_report,
            cabinet_stability_report=stability_report,
            hardware_placement_report=hardware_report,
            kitchen_manufacturing_report=kitchen_report,
        )
        capacity_intelligence_report = (
            FactoryCapacityIntelligenceBuilder().build(
                FactoryResourceReport(weekly_capacity_hours=0.05),
                ManufacturingDurationReport(
                    total_production_minutes=simulation_report.estimated_total_factory_minutes,
                ),
            )
        )
        executive_intelligence_report = (
            FactoryExecutiveIntelligenceBuilder().build(
                capacity_intelligence_report,
                load_report,
                bottleneck_report,
                delivery_intelligence_report,
                factory_capacity_simulation_report=capacity_simulation_report,
                production_forecast_report=forecast_report,
                factory_delivery_report=delivery_report,
            )
        )
        executive_decision_report = FactoryExecutiveDecisionBuilder().build(
            profitability_report,
            delivery_report,
            readiness_report,
        )
        operational_report = FactoryOperationalBuilder().build(
            readiness_report,
            schedule_report,
            bottleneck_report,
        )

        self.assertEqual(readiness_report.readiness_status, "BLOCKED")
        self.assertEqual(capacity_simulation_report.capacity_status, "OVERLOADED")
        self.assertEqual(capacity_intelligence_report.status, "OVERLOADED")
        self.assertEqual(forecast_report.forecast_status, "DELAY_RISK")
        self.assertEqual(executive_intelligence_report.factory_status, "CRITICAL")
        self.assertEqual(executive_intelligence_report.main_bottleneck, "CNC")
        self.assertEqual(
            executive_intelligence_report.priority_action,
            "Increase CNC availability",
        )
        self.assertEqual(executive_decision_report.business_status, "REJECT")
        self.assertEqual(
            executive_decision_report.executive_recommendation,
            "Project should not enter production",
        )
        self.assertEqual(operational_report.operational_status, "BLOCKED")
        self.assertEqual(
            operational_report.management_recommendation,
            "Project should not enter production",
        )

        self.assertEqual(
            [
                self._snapshot(manufacturing_package),
                self._snapshot(structural_report),
                self._snapshot(stability_report),
                self._snapshot(hardware_report),
                self._snapshot(kitchen_report),
                self._snapshot(profitability_report),
                self._snapshot(delivery_report),
                self._snapshot(schedule_report),
                self._snapshot(load_report),
                self._snapshot(bottleneck_report),
                self._snapshot(delivery_intelligence_report),
            ],
            snapshots,
        )

    @staticmethod
    def _manufacturing_package():
        from manufacturing.manufacturing_cutlist_report import (
            ManufacturingCutlistReport,
        )
        from manufacturing.manufacturing_edge_report import (
            ManufacturingEdgeReport,
        )
        from manufacturing.manufacturing_machining_report import (
            ManufacturingMachiningReport,
        )
        from manufacturing.manufacturing_package import ManufacturingPackage

        return ManufacturingPackage(
            panels=[
                SimpleNamespace(
                    identity="panel-01",
                    width=100.0,
                    height=200.0,
                    thickness=18.0,
                    material="MDF",
                    quantity=1,
                )
            ],
            materials=[SimpleNamespace(name="MDF", thickness=18.0)],
            machining_operations=[
                SimpleNamespace(operation_type="DRILL", source="panel-01")
            ],
            edge_operations=[
                SimpleNamespace(operation_type="EDGE_BANDING", source="panel-01")
            ],
            warnings=[],
        )

    @staticmethod
    def _structural_report(structural_risk="LOW"):
        return SimpleNamespace(
            structural_risk=structural_risk,
            stability_risk="LOW",
            tags=[],
        )

    @staticmethod
    def _stability_report():
        return SimpleNamespace(
            tipping_risk="LOW",
            large_span_risk="LOW",
            tags=[],
        )

    @staticmethod
    def _hardware_report():
        return SimpleNamespace(hardware_risk="LOW", tags=[])

    @staticmethod
    def _kitchen_report():
        return SimpleNamespace(
            manufacturing_complexity="LOW",
            cabinet_count=1,
            tags=[],
        )

    @staticmethod
    def _profitability_report():
        from cost_intelligence.profitability_report import ProfitabilityReport

        return ProfitabilityReport(profitability_status="LOW")

    @staticmethod
    def _delivery_report(delivery_status="ON_TRACK"):
        from manufacturing.factory_delivery_report import FactoryDeliveryReport

        return FactoryDeliveryReport(delivery_status=delivery_status)

    @staticmethod
    def _schedule_report(schedule_risk_level="LOW"):
        from manufacturing.production_schedule_report import (
            ProductionScheduleReport,
        )

        return ProductionScheduleReport(schedule_risk_level=schedule_risk_level)

    @staticmethod
    def _load_report(status="LOW", bottleneck=""):
        from manufacturing.factory_load_report import FactoryLoadReport

        return FactoryLoadReport(status=status, bottleneck=bottleneck)

    @staticmethod
    def _bottleneck_report(
        bottleneck="",
        severity="LOW",
        recommendation="No bottleneck detected",
    ):
        from manufacturing.factory_bottleneck_intelligence_report import (
            FactoryBottleneckIntelligenceReport,
        )

        return FactoryBottleneckIntelligenceReport(
            bottleneck=bottleneck,
            severity=severity,
            recommendation=recommendation,
        )

    @staticmethod
    def _delivery_intelligence_report():
        from manufacturing.delivery_intelligence_report import (
            DeliveryIntelligenceReport,
        )

        return DeliveryIntelligenceReport(
            confidence="LOW",
            delivery_risk="HIGH",
            recommendation="Review delivery plan",
        )

    @staticmethod
    def _snapshot(report):
        return {
            key: list(value) if isinstance(value, list) else value
            for key, value in report.__dict__.items()
        }


if __name__ == "__main__":
    unittest.main()
