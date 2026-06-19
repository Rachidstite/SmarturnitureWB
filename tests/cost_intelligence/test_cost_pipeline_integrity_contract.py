from dataclasses import fields

from cost_intelligence.cost_estimate import CostEstimate
from cost_intelligence.cost_report import CostReport
from cost_intelligence.cost_summary_calculator import CostSummaryCalculator
from cost_intelligence.manufacturing_cost_report import (
    ManufacturingCostReport,
)
from cost_intelligence.manufacturing_cost_summary import (
    ManufacturingCostSummary,
)
from cost_intelligence.profitability_calculator import ProfitabilityCalculator
from cost_intelligence.profitability_report import ProfitabilityReport
from cost_intelligence.quotation_calculator import QuotationCalculator
from cost_intelligence.quotation_report import QuotationReport


def _field_names(model):
    return [field.name for field in fields(model)]


def _cost_field_names(model):
    return [name for name in _field_names(model) if name.endswith("_cost")]


def test_cost_pipeline_integrity_contract():
    cost_estimate_fields = _field_names(CostEstimate)
    manufacturing_cost_report_fields = _field_names(ManufacturingCostReport)
    cost_report_fields = _field_names(CostReport)
    quotation_report_fields = _field_names(QuotationReport)
    profitability_report_fields = _field_names(ProfitabilityReport)
    manufacturing_cost_summary_fields = _field_names(ManufacturingCostSummary)

    estimate = CostSummaryCalculator().estimate(
        material_estimate=CostEstimate(material_cost=50.0, total_cost=50.0),
        sheet_estimate=CostEstimate(sheet_cost=560.0, total_cost=560.0),
        waste_estimate=CostEstimate(waste_cost=84.0, total_cost=84.0),
        hardware_estimate=CostEstimate(hardware_cost=48.0, total_cost=48.0),
    )

    cost_report = CostReport.from_estimate(estimate)
    quotation_report = QuotationCalculator(markup_rate=0.25).build(cost_report)
    profitability_report = ProfitabilityCalculator().build(quotation_report)

    cost_estimate_cost_fields = _cost_field_names(CostEstimate)
    manufacturing_cost_report_cost_fields = _cost_field_names(
        ManufacturingCostReport
    )
    cost_report_cost_fields = _cost_field_names(CostReport)
    quotation_report_cost_fields = _cost_field_names(QuotationReport)
    profitability_report_cost_fields = _cost_field_names(ProfitabilityReport)
    manufacturing_cost_summary_cost_fields = _cost_field_names(
        ManufacturingCostSummary
    )

    duplicate_cost_fields = {
        name: [
            model_name
            for model_name, model_fields in (
                ("CostEstimate", cost_estimate_fields),
                (
                    "ManufacturingCostReport",
                    manufacturing_cost_report_fields,
                ),
                ("CostReport", cost_report_fields),
                ("QuotationReport", quotation_report_fields),
                ("ProfitabilityReport", profitability_report_fields),
                (
                    "ManufacturingCostSummary",
                    manufacturing_cost_summary_fields,
                ),
            )
            if name in model_fields
        ]
        for name in sorted(
            set(cost_estimate_cost_fields)
            | set(manufacturing_cost_report_cost_fields)
            | set(cost_report_cost_fields)
            | set(quotation_report_cost_fields)
            | set(profitability_report_cost_fields)
            | set(manufacturing_cost_summary_cost_fields)
        )
        if sum(
            name in model_fields
            for model_fields in (
                cost_estimate_fields,
                manufacturing_cost_report_fields,
                cost_report_fields,
                quotation_report_fields,
                profitability_report_fields,
                manufacturing_cost_summary_fields,
            )
        )
        > 1
    }

    ignored_cost_fields = {
        "CostSummaryCalculator.estimate": [
            "material_cost",
            "waste_cost",
        ],
        "ManufacturingCostCalculator.calculate": [
            "material_cost",
            "edge_banding_cost",
            "drilling_cost",
            "complexity_cost",
            "panel_handling_cost",
        ],
        "ManufacturingCostSummaryBuilder.build": [
            "cost_report",
            "risk_report",
            "insights",
            "risk_level",
            "warnings",
        ],
    }

    exact_pipeline_ownership = {
        "CostSummaryCalculator.estimate": {
            "material_cost": "material_estimate.material_cost",
            "sheet_cost": "sheet_estimate.sheet_cost",
            "waste_cost": "waste_estimate.waste_cost",
            "hardware_cost": "hardware_estimate.hardware_cost",
            "total_cost": "sheet_cost + hardware_cost",
        },
        "CostReport.from_estimate": {
            "material_cost": "estimate.material_cost",
            "sheet_cost": "estimate.sheet_cost",
            "waste_cost": "estimate.waste_cost",
            "hardware_cost": "estimate.hardware_cost",
            "total_cost": "estimate.total_cost",
            "currency": "estimate.currency",
            "warnings": "list(estimate.warnings)",
        },
        "QuotationCalculator.build": {
            "production_cost": "cost_report.total_cost",
            "markup_rate": "self.markup_rate",
            "markup_amount": "production_cost * self.markup_rate",
            "selling_price": "production_cost + markup_amount",
            "currency": "cost_report.currency",
        },
        "ProfitabilityCalculator.build": {
            "production_cost": "quotation_report.production_cost",
            "selling_price": "quotation_report.selling_price",
            "gross_profit": "selling_price - production_cost",
            "gross_margin_rate": "gross_profit / selling_price if selling_price > 0 else 0",
            "profitability_status": "LOW/MEDIUM/HIGH from gross_margin_rate",
            "currency": "quotation_report.currency",
            "warnings": "list(quotation_report.warnings)",
        },
            "ManufacturingCostSummaryBuilder.build": {
                "cost_report": "cost_report",
                "risk_report": "risk_report",
                "insights": "insights",
                "total_manufacturing_cost": "cost_report.total_manufacturing_cost",
                "hardware_cost": "cost_report.hardware_cost",
                "risk_level": "risk_report.risk_level",
                "warnings": "risk_report.warnings",
            },
        }

    assert "hardware_cost" in manufacturing_cost_report_fields
    assert "hardware_cost" in manufacturing_cost_summary_fields
    assert cost_report.total_cost == 608.0
    assert quotation_report.production_cost == 608.0
    assert profitability_report.production_cost == 608.0
    assert exact_pipeline_ownership["ManufacturingCostSummaryBuilder.build"][
        "hardware_cost"
    ] == "cost_report.hardware_cost"
    assert duplicate_cost_fields["hardware_cost"] == [
        "CostEstimate",
        "ManufacturingCostReport",
        "CostReport",
        "ManufacturingCostSummary",
    ]
