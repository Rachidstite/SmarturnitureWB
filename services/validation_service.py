from shared.issues import ValidationState; from engine.geometry_engine import GeometryEngine
class ValidationService:
    def __init__(self, cabinet, mat): self.geo = GeometryEngine(cabinet, mat)
    def validate_only(self) -> ValidationState:
        self.geo.resolve_all(); state = ValidationState(); state.issues = self.geo.issues; return state
