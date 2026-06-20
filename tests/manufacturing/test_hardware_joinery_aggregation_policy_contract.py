import inspect
from dataclasses import fields


def test_hardware_intelligence_keeps_family_detail_fields():
    from manufacturing.hardware_intelligence_report import HardwareIntelligenceReport

    field_names = [field.name for field in fields(HardwareIntelligenceReport)]

    assert "hardware_family" in field_names
    assert "total_hardware_items" in field_names
    assert "total_host_holes" in field_names
    assert "total_target_holes" in field_names
    assert "requires_review" in field_names
    assert "manufacturing_warning" in field_names
    assert "recommended_action" in field_names


def test_joinery_intelligence_exposes_only_project_level_aggregate_fields():
    from manufacturing.joinery_intelligence_report import JoineryIntelligenceReport

    assert [field.name for field in fields(JoineryIntelligenceReport)] == [
        "total_minifix",
        "total_hinges",
        "total_drawer_slides",
        "total_handles",
        "total_face_holes",
        "total_edge_holes",
        "total_cam_holes",
        "joinery_complexity_score",
        "warnings",
    ]


def test_recommended_action_does_not_cross_into_joinery_report():
    from manufacturing.joinery_intelligence_report import JoineryIntelligenceReport

    field_names = [field.name for field in fields(JoineryIntelligenceReport)]

    assert "recommended_action" not in field_names
    assert "manufacturing_warning" not in field_names
    assert "requires_review" not in field_names


def test_host_and_target_hole_detail_do_not_cross_into_joinery_report():
    from manufacturing.joinery_intelligence_report import JoineryIntelligenceReport

    field_names = [field.name for field in fields(JoineryIntelligenceReport)]

    assert "total_host_holes" not in field_names
    assert "total_target_holes" not in field_names


def test_joinery_builder_keeps_compiled_face_and_edge_holes_as_source_of_truth():
    import manufacturing.joinery_intelligence_builder as module

    source = inspect.getsource(module)

    assert "machining_ops" in source
    assert 'getattr(project.graph, "physical_nodes", [])' in source
    assert "HardwareIntelligenceBuilder" not in source
    assert "HardwareIntelligenceReport" not in source
    assert "hardware_intelligence" not in source
    assert "total_face_holes = sum(" in source
    assert "total_edge_holes = sum(" in source


def test_joinery_builder_family_counts_remain_joinery_level_aggregates_only():
    import manufacturing.joinery_intelligence_builder as module

    source = inspect.getsource(module)

    assert "total_minifix" in source
    assert "total_hinges" in source
    assert "total_drawer_slides" in source
    assert "total_handles" in source
    assert "hardware_family" not in source
    assert "recommended_action" not in source
    assert "total_host_holes" not in source
    assert "total_target_holes" not in source


def test_hardware_joinery_integration_remains_postponed_in_builder_contract():
    from manufacturing.joinery_intelligence_builder import JoineryIntelligenceBuilder

    build_signature = inspect.signature(JoineryIntelligenceBuilder.build)

    assert list(build_signature.parameters) == ["self", "project"]
