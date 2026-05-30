from .equal_layout import EqualLayoutStrategy; from .manual_layout import ManualLayoutStrategy
from shared.enums import DrawerLayoutMode, DoorType; from .layout_context import LayoutContext; from .layout_result import LayoutResult, DoorZone, ShelfZone, LayoutDiagnostics; from .policies import DefaultWardrobePolicy
LAYOUT_REGISTRY = {DrawerLayoutMode.MANUAL: ManualLayoutStrategy, DrawerLayoutMode.EQUAL: EqualLayoutStrategy}
class LayoutEngine:
    def __init__(self, registry=None, policy=None): self.registry = registry or LAYOUT_REGISTRY; self.policy = policy or DefaultWardrobePolicy()
    def resolve_zones(self, context: LayoutContext) -> LayoutResult:
        n = context.section_config.drawers; door_type = context.door_type; mat = context.mat; drawer_result = LayoutResult()
        if n > 0:
            drawer_zone_height = context.available_height * self.policy.drawer_zone_ratio if door_type != DoorType.NONE else context.available_height
            drawer_context = LayoutContext(params=context.params, section_config=context.section_config, mat=context.mat,
                                           available_height=drawer_zone_height, base_z=context.base_z,
                                           door_type=context.door_type, has_sliding=context.has_sliding,
                                           sliding_track=context.sliding_track)
            mode = context.section_config.drawer_layout_mode; strategy = self.registry.get(mode, ManualLayoutStrategy)()
            drawer_result = strategy.resolve(drawer_context)
        door_zone = None
        if door_type != DoorType.NONE:
            consumed = drawer_result.diagnostics.consumed_height if drawer_result.diagnostics else 0.0
            door_start = context.base_z + consumed
            door_height = context.available_height - consumed - mat.door_top_gap - mat.door_bottom_gap
            if door_height > 0: door_zone = DoorZone(height=door_height, z_start=door_start + mat.door_bottom_gap)
        shelf_zone = None
        if context.section_config.shelves > 0 and door_zone: shelf_zone = ShelfZone(height=door_zone.height,
                                                                                     z_start=door_zone.z_start)
        diagnostics = LayoutDiagnostics(
            consumed_height=drawer_result.diagnostics.consumed_height if drawer_result.diagnostics else 0.0,
            remaining_height=context.available_height - (
                drawer_result.diagnostics.consumed_height if drawer_result.diagnostics else 0.0),
            normalization_loss=drawer_result.diagnostics.normalization_loss if drawer_result.diagnostics else 0.0,
            warnings=drawer_result.diagnostics.warnings if drawer_result.diagnostics else [])
        return LayoutResult(drawer_zones=drawer_result.drawer_zones, door_zone=door_zone, shelf_zone=shelf_zone,
                            diagnostics=diagnostics)
