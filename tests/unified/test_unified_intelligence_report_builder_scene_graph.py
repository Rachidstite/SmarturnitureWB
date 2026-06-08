from unittest.mock import patch


@patch(
    "validation.intelligence.unified.unified_intelligence_report_builder.EngineeringIntelligenceReportBuilder"
)
def test_scene_graph_forwarded_to_engineering_builder(
    engineering_builder_cls,
):

    engineering_builder_cls.return_value.build.return_value = object()

    from validation.intelligence.unified.unified_intelligence_report_builder import (
        UnifiedIntelligenceReportBuilder,
    )

    try:
        UnifiedIntelligenceReportBuilder().build(
            [],
            scene_graph="graph",
        )
    except Exception:
        pass

    args, kwargs = (
        engineering_builder_cls.return_value.build.call_args
    )

    assert kwargs["scene_graph"] == "graph"
