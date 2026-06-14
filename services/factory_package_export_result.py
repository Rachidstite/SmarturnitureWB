from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class FactoryPackageExportResult:
    project_intelligence_result: Any
    executive_report_path: Path
    release_summary_path: Path
