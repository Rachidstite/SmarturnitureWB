from unittest.mock import patch

from services.project_intelligence_service import (
    ProjectIntelligenceService,
)


@patch(
    "services.project_intelligence_service.HybridManufacturingExtractor"
)
def test_project_pipeline_returns_dashboard(
    extractor_cls,
):

    extractor_cls.extract.return_value = [
        object()
    ]

    result = (
        ProjectIntelligenceService.build(
            object()
        )
    )

    assert result is not None

    assert result.report is not None

    assert result.viewmodel is not None

    assert result.state is not None
