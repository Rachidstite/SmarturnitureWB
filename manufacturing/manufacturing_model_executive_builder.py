from manufacturing.manufacturing_executive_builder import (
    ManufacturingExecutiveBuilder,
)
from manufacturing.manufacturing_model_builder import ManufacturingModelBuilder
from manufacturing.manufacturing_model_executive_result import (
    ManufacturingModelExecutiveResult,
)


class ManufacturingModelExecutiveBuilder:

    def build(
        self,
        manufacturing_model_inputs=None,
        executive_inputs=None,
        inventory_counts=None,
    ):
        manufacturing_model_kwargs = dict(manufacturing_model_inputs or {})
        if inventory_counts is not None:
            manufacturing_model_kwargs["inventory_counts"] = inventory_counts

        manufacturing_model_report = ManufacturingModelBuilder().build(
            **manufacturing_model_kwargs,
        )

        manufacturing_executive_report = ManufacturingExecutiveBuilder().build(
            manufacturing_model_report,
            **dict(executive_inputs or {}),
        )

        return ManufacturingModelExecutiveResult(
            manufacturing_model_report=manufacturing_model_report,
            manufacturing_executive_report=manufacturing_executive_report,
        )
