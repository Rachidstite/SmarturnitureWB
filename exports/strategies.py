from typing import List
from dataclasses import dataclass, field

from cost_intelligence.remaining_region import RemainingRegion

@dataclass
class PlacedPart:
    part: any
    x: float
    y: float
    placed_width: float
    placed_height: float
    rotated: bool
    cross_cut_x: float = 0.0  # إحداثي القص العرضي للقطعة

@dataclass
class StripNode:
    y_start: float
    height: float
    rip_cut_y: float = 0.0    # إحداثي القص الطولي للشريحة
    parts: List[PlacedPart] = field(default_factory=list)

@dataclass
class SheetResult:
    sheet_id: int
    used_area: float = 0.0
    placed_parts: List[PlacedPart] = field(default_factory=list)
    strips: List[StripNode] = field(default_factory=list)
    material: str = ""
    thickness: float = 0.0
    sheet_width: float = 0.0
    sheet_height: float = 0.0
    kerf: float = 0.0
    trim: float = 0.0
    remaining_regions: list = field(default_factory=list)

class PlacementStrategy:
    def pack(self, parts: list, sheet_w: float, sheet_h: float, kerf: float) -> List[SheetResult]:
        raise NotImplementedError

class GuillotineStripStrategy(PlacementStrategy):
    def __init__(self, trim_cut: float = 10.0):
        self.trim = trim_cut 

    def pack(self, parts: list, sheet_w: float, sheet_h: float, kerf: float, material: str = "", thickness: float = 0.0) -> List[SheetResult]:
        parts.sort(key=lambda p: max(p.width, p.height), reverse=True)
        sheets = []
        current_sheet = SheetResult(
            sheet_id=1,
            material=material,
            thickness=thickness,
            sheet_width=sheet_w,
            sheet_height=sheet_h,
            kerf=kerf,
            trim=self.trim,
        )
        current_y = self.trim
        current_strip = None
        
        for part in parts:
            p_w, p_h = part.width, part.height
            rotated = False
            
            if part.can_rotate and p_h > p_w:
                p_w, p_h = p_h, p_w
                rotated = True
                
            if p_w > (sheet_w - 2*self.trim) or p_h > (sheet_h - 2*self.trim):
                continue

            placed = False
            if current_strip and p_h <= current_strip.height:
                last_x = self.trim
                if current_strip.parts:
                    last_part = current_strip.parts[-1]
                    last_x = last_part.x + last_part.placed_width + kerf
                    
                if last_x + p_w <= (sheet_w - self.trim):
                    placed_part = PlacedPart(part, last_x, current_y, p_w, p_h, rotated)
                    placed_part.cross_cut_x = last_x + p_w
                    current_strip.parts.append(placed_part)
                    current_sheet.placed_parts.append(placed_part)
                    current_sheet.used_area += (p_w * p_h)
                    placed = True

            if not placed:
                if current_strip:
                    current_y += current_strip.height + kerf
                    
                if current_y + p_h <= (sheet_h - self.trim):
                    current_strip = StripNode(y_start=current_y, height=p_h)
                    current_strip.rip_cut_y = current_y + p_h
                    current_sheet.strips.append(current_strip)
                    
                    placed_part = PlacedPart(part, self.trim, current_y, p_w, p_h, rotated)
                    placed_part.cross_cut_x = self.trim + p_w
                    current_strip.parts.append(placed_part)
                    current_sheet.placed_parts.append(placed_part)
                    current_sheet.used_area += (p_w * p_h)
                else:
                    self._populate_remaining_regions(
                        current_sheet,
                    )
                    sheets.append(current_sheet)
                    current_sheet = SheetResult(
                        sheet_id=len(sheets) + 1,
                        material=material,
                        thickness=thickness,
                        sheet_width=sheet_w,
                        sheet_height=sheet_h,
                        kerf=kerf,
                        trim=self.trim,
                    )
                    current_y = self.trim
                    current_strip = StripNode(y_start=current_y, height=p_h)
                    current_strip.rip_cut_y = current_y + p_h
                    current_sheet.strips.append(current_strip)
                    
                    placed_part = PlacedPart(part, self.trim, current_y, p_w, p_h, rotated)
                    placed_part.cross_cut_x = self.trim + p_w
                    current_strip.parts.append(placed_part)
                    current_sheet.placed_parts.append(placed_part)
                    current_sheet.used_area += (p_w * p_h)

        if current_sheet.placed_parts:
            self._populate_remaining_regions(
                current_sheet,
            )
            sheets.append(current_sheet)
            
        return sheets

    def _populate_remaining_regions(
        self,
        sheet,
    ):
        source_sheet = f"SHEET-{sheet.sheet_id}"
        region_number = 1
        usable_right = sheet.sheet_width - sheet.trim
        usable_bottom = sheet.sheet_height - sheet.trim

        for strip in sheet.strips:
            if not strip.parts:
                continue

            last_part = strip.parts[-1]
            width = usable_right - last_part.cross_cut_x

            if width > 0 and strip.height > 0:
                sheet.remaining_regions.append(
                    RemainingRegion(
                        id=f"{source_sheet}-REGION-{region_number}",
                        x=last_part.cross_cut_x,
                        y=strip.y_start,
                        width=width,
                        height=strip.height,
                        source_sheet=source_sheet,
                    )
                )
                region_number += 1

        if sheet.strips:
            last_strip = sheet.strips[-1]
            y = last_strip.rip_cut_y + sheet.kerf
            width = sheet.sheet_width - (2 * sheet.trim)
            height = usable_bottom - y

            if width > 0 and height > 0:
                sheet.remaining_regions.append(
                    RemainingRegion(
                        id=f"{source_sheet}-REGION-{region_number}",
                        x=sheet.trim,
                        y=y,
                        width=width,
                        height=height,
                        source_sheet=source_sheet,
                    )
                )
