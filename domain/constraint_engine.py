from domain.diagnostics import ValidationReport, ConstraintViolation, Severity
from domain.spatial_queries import SpatialQueryEngine

class CabinetConstraintValidator:
    def __init__(self, project):
        self.project = project
        self.report = ValidationReport()
        self.spatial_engine = SpatialQueryEngine(getattr(self.project.graph, 'physical_nodes', []))

    def _check_section_widths(self):
        if not hasattr(self.project, 'topology'): return
        for uid, sec in self.project.topology.sections.items():
            if sec.width < 100:
                sev = Severity.FATAL if sec.width <= 0 else Severity.ERROR
                self.report.add(ConstraintViolation(
                    code="SECTION_TOO_SMALL", message="Section width is too small.",
                    severity=sev, node_id=uid, current_value=sec.width, required_value=100.0
                ))

    
    def _check_shelf_deflection(self):
        """
        Legacy rule removed.

        Shelf span validation now lives in:
        - ShelfSagRule
        - DividerSpacingRule

        using PanelSpec.span.
        """
        return

    def _check_collisions(self):
        collisions = self.spatial_engine.find_collisions()
        for id1, id2 in collisions:
            self.report.add(ConstraintViolation(
                code="PHYSICAL_COLLISION", message=f"Collision between {id1} and {id2}.",
                severity=Severity.ERROR, node_id=f"{id1} / {id2}"
            ))

    def _check_dangling_joinery(self):
        if not hasattr(self.project, 'joinery'): return
        existing_nodes = {n.identity.key for n in self.project.graph.nodes}
        valid_anchors = existing_nodes
        for edge in self.project.joinery.edges:
            if edge.source_id not in valid_anchors:
                self.report.add(ConstraintViolation(
                    code="DANGLING_JOINERY_REFERENCE", message=f"Missing node: {edge.source_id}",
                    severity=Severity.FATAL, node_id=edge.target_id
                ))

    def _check_machining_limits(self):
        """⚡ Smart Manufacturing Validation Layer"""
        for node in getattr(self.project.graph, 'physical_nodes', []):
            for op in getattr(node, 'machining_ops', []):
                face = op.face.upper() if hasattr(op, 'face') and op.face else "FRONT"
                
                # 1. تحديد الحد الأقصى للعمق بناءً على الوجه المستهدف (Spatial Awareness)
                if face in ["FRONT", "BACK"]:
                    max_depth = node.thickness
                elif face in ["LEFT", "RIGHT"]:
                    max_depth = node.width
                elif face in ["TOP", "BOTTOM"]:
                    max_depth = node.height
                else:
                    max_depth = node.thickness

                # 2. الفحص الذكي للعمق
                if not getattr(op, 'is_through', False) and op.depth >= max_depth:
                    self.report.add(ConstraintViolation(
                        code="HOLE_TOO_DEEP", 
                        message=f"Hole depth ({op.depth}mm) exceeds max allowed ({max_depth}mm) on face {face}.",
                        severity=Severity.FATAL, node_id=node.identity.key, 
                        current_value=op.depth, required_value=max_depth - 1.0
                    ))
                
                # 3. فحص الحدود (لثقوب الوجه فقط حالياً)
                if face in ["FRONT", "BACK"]:
                    safe_margin = op.diameter / 2.0
                    if op.local_x < safe_margin or op.local_x > (node.width - safe_margin) or \
                       op.local_y < safe_margin or op.local_y > (node.height - safe_margin):
                        self.report.add(ConstraintViolation(
                            code="HOLE_OUT_OF_BOUNDS", message="Hole violates safe margins.",
                            severity=Severity.ERROR, node_id=node.identity.key
                        ))

    def _check_racking_stability(self):
        """
        Legacy rule removed.

        Back panel validation now lives in:
        - BackPanelRequiredRule
        """
        return



    def validate_all(self) -> ValidationReport:
        self._check_section_widths()
        self._check_shelf_deflection()
        self._check_collisions()
        self._check_dangling_joinery()
        self._check_machining_limits()
        self._check_racking_stability() # ⚡ تفعيل حماية الترخيم
        return self.report