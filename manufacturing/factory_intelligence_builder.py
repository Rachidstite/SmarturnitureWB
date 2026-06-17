from manufacturing.factory_capacity_intelligence_builder import (
    FactoryCapacityIntelligenceBuilder,
)
from manufacturing.factory_load_builder import FactoryLoadBuilder
from manufacturing.factory_intelligence_report import FactoryIntelligenceReport
from manufacturing.factory_resource_builder import FactoryResourceBuilder


class FactoryIntelligenceBuilder:

    def __init__(
        self,
        factory_resource_builder=None,
        factory_capacity_builder=None,
        factory_load_builder=None,
    ):
        self.factory_resource_builder = (
            factory_resource_builder or FactoryResourceBuilder()
        )
        self.factory_capacity_builder = (
            factory_capacity_builder or FactoryCapacityIntelligenceBuilder()
        )
        self.factory_load_builder = (
            factory_load_builder or FactoryLoadBuilder()
        )

    def build(self, manufacturing_duration_report):
        factory_resource_report = self.factory_resource_builder.build()
        factory_capacity_report = self.factory_capacity_builder.build(
            factory_resource_report,
            manufacturing_duration_report,
        )
        factory_load_report = self.factory_load_builder.build(
            factory_resource_report,
            manufacturing_duration_report,
        )

        return FactoryIntelligenceReport(
            factory_resource_report=factory_resource_report,
            factory_capacity_report=factory_capacity_report,
            factory_load_report=factory_load_report,
        )
