from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class Severity(Enum):
    INFO = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

@dataclass
class ConstraintViolation:
    """يمثل خرقاً لقيد صناعي أو هندسي (بيانات مهيكلة بدلاً من نصوص)"""
    code: str
    message: str
    severity: Severity = Severity.ERROR
    
    node_id: Optional[str] = None
    
    current_value: Optional[float] = None
    required_value: Optional[float] = None
    
    suggestion: str = ""

class ValidationReport:
    """حاوية تجمع كل التقارير وتوفر واجهة استعلام سهلة للـ UI والـ Pipeline"""
    def __init__(self):
        self.violations: List[ConstraintViolation] = []

    def add(self, violation: ConstraintViolation):
        self.violations.append(violation)

    @property
    def has_errors(self) -> bool:
        return any(v.severity in (Severity.ERROR, Severity.FATAL) for v in self.violations)

    @property
    def has_fatals(self) -> bool:
        return any(v.severity == Severity.FATAL for v in self.violations)
        
    def get_errors(self) -> List[ConstraintViolation]:
        return [v for v in self.violations if v.severity in (Severity.ERROR, Severity.FATAL)]

    def print_summary(self):
        """طباعة ملخص للـ CLI (يستخدم كبديل مؤقت للـ UI)"""
        print(f"\n📋 VALIDATION REPORT: {len(self.violations)} Issues Found")
        print("-" * 50)
        for v in self.violations:
            icon = "🔴" if v.severity in (Severity.ERROR, Severity.FATAL) else "🟡" if v.severity == Severity.WARNING else "🔵"
            print(f"{icon} [{v.severity.name}] {v.code} | Node: {v.node_id}")
            print(f"   ➤ {v.message}")
            if v.current_value is not None and v.required_value is not None:
                print(f"   📊 Current: {v.current_value} | Required: {v.required_value}")
            if v.suggestion:
                print(f"   💡 Suggestion: {v.suggestion}")
            print()
