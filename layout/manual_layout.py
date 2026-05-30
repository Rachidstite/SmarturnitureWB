from .base_layout import DrawerLayoutStrategy; from .layout_context import LayoutContext; from .layout_result import LayoutResult, DrawerZone, LayoutDiagnostics
class ManualLayoutStrategy(DrawerLayoutStrategy):
    def resolve(self, context: LayoutContext) -> LayoutResult:
        heights = getattr(context.section_config, "drawer_heights", []) or []
        n = context.section_config.drawers
        if n <= 0: return LayoutResult()
        if len(heights) != n: heights = [context.mat.default_drawer_height] * n
        zones = []; current_z = context.base_z
        for i, h in enumerate(heights): zones.append(DrawerZone(height=h, z_start=current_z, index=i)); current_z += h + context.mat.clearance
        remaining = context.available_height - (current_z - context.base_z)
        return LayoutResult(drawer_zones=zones, diagnostics=LayoutDiagnostics(consumed_height=current_z-context.base_z, remaining_height=remaining))
