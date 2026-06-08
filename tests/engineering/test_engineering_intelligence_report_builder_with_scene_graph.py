from types import SimpleNamespace

from validation.intelligence.engineering.engineering_intelligence_report_builder import (
    EngineeringIntelligenceReportBuilder,
)

from shared.roles import NodeRole


def test_builder_includes_assembly_rule_results():

    panel_specs = []

    scene_graph = SimpleNamespace(
        physical_nodes=[
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2600,
            ),
            SimpleNamespace(
                role=NodeRole.SIDE_PANEL,
                height=2600,
            ),
        ]
    )

    report = (
        EngineeringIntelligenceReportBuilder()
        .build(
            panel_specs,
            scene_graph=scene_graph,
        )
    )

    assert len(report.errors) > 0
