import math
from .base_layout import DrawerLayoutStrategy; from .layout_context import LayoutContext; from .layout_result import LayoutResult, DrawerZone, LayoutDiagnostics; from .normalizer import DimensionNormalizer, NormalizationMode
class EqualLayoutStrategy(DrawerLayoutStrategy):
    def resolve(self, context: LayoutContext) -> LayoutResult:
        n = context.section_config.drawers
        if n <= 0: return LayoutResult()
        total_gaps = context.mat.clearance * (n - 1); available = context.available_height - total_gaps
        if available <= 0: return LayoutResult(diagnostics=LayoutDiagnostics(warnings=["Drawer zone too small"]))
        raw_h = available / n; normalized_h = DimensionNormalizer.round_to_increment(raw_h, 5.0, NormalizationMode.FLOOR)
        heights = [normalized_h] * n; total_normalized = sum(heights) + total_gaps; diff = context.available_height - total_normalized
        if diff > 0:
            fraction = diff / n; extra = 0.0
            for i in range(n):
                extra += fraction
                if extra >= 1.0: heights[i] += int(extra); extra -= int(extra)
        zones = []; current_z = context.base_z
        for i, h in enumerate(heights): zones.append(DrawerZone(height=h, z_start=current_z, index=i)); current_z += h + context.mat.clearance
        remaining = context.available_height - (current_z - context.base_z)
        return LayoutResult(drawer_zones=zones, diagnostics=LayoutDiagnostics(consumed_height=sum(heights)+total_gaps, remaining_height=remaining, normalization_loss=abs(raw_h*n - sum(heights))))
