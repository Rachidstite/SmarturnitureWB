import FreeCAD as App, Part
from domain.system32 import System32Engine
class DoorBuilder:
    @staticmethod
    def build(doc, group, name, fw, fh, px, py, pz, mat, door_type_str,
              cnc_engine=None, hw_builder=None, hw_group=None, hinge_side="LEFT", door_layer=0):
        is_glass = "Glass" in door_type_str; base_type = "Inset"
        if "Overlay" in door_type_str: base_type = "Overlay"
        elif "Sliding" in door_type_str: base_type = "Sliding"
        if is_glass:
            subgroup = doc.addObject("App::DocumentObjectGroup", name); group.addObject(subgroup)
            fw2 = mat.glass_frame_width; frame = doc.addObject("Part::Feature", f"{name}_Frame")
            outer = Part.makeBox(fw, mat.mdf_thickness, fh)
            inner = Part.makeBox(fw - 2 * fw2, mat.mdf_thickness, fh - 2 * fw2)
            inner.Placement = App.Placement(App.Vector(fw2, 0, fw2), App.Rotation()); shape = outer.cut(inner)
            if cnc_engine and base_type != "Sliding": shape = cnc_engine.drill_hinge_cup(shape, fh)
            frame.Shape = shape; frame.Placement = App.Placement(App.Vector(px, py, pz), App.Rotation())
            frame.ViewObject.ShapeColor = (0.2, 0.2, 0.25); subgroup.addObject(frame)
            glass = doc.addObject("Part::Feature", f"{name}_Glass")
            glass.Shape = Part.makeBox(fw - 2 * fw2, 4, fh - 2 * fw2)
            glass.Placement = App.Placement(App.Vector(px + fw2, py + (mat.mdf_thickness - 4) / 2, pz + fw2),
                                            App.Rotation())
            glass.ViewObject.ShapeColor = (0.6, 0.8, 0.95); glass.ViewObject.Transparency = 65; subgroup.addObject(glass)
        else:
            door = doc.addObject("Part::Feature", name); shape = Part.makeBox(fw, mat.mdf_thickness, fh)
            if cnc_engine and base_type != "Sliding": shape = cnc_engine.drill_hinge_cup(shape, fh)
            door.Shape = shape
            door.Placement = App.Placement(App.Vector(px, py, pz), App.Rotation())
            door.ViewObject.ShapeColor = (0.5, 0.5, 0.5) if base_type == "Sliding" else (0.6, 0.4, 0.2)

            if not hasattr(door, "SmartUUID"):
                door.addProperty("App::PropertyString", "SmartUUID")

            door.SmartUUID = name

            group.addObject(door)
        if hw_builder and hw_group and base_type != "Sliding":
            
            hy = py + mat.mdf_thickness

            # HINGE DEBUG MOVED
            if hinge_side == "LEFT":
                hx = px + 22.5
            else:
                hx = px + fw - 22.5

            print(f"[HINGE DEBUG] {name} side={hinge_side} hx={hx}")
            print(f"[HINGE SIDE] {name} hinge_side={hinge_side}")
            print(f"[HINGE SIDE] {name} hinge_side={hinge_side}")

            hinge_positions = System32Engine.hinge_positions(fh)

            for idx, pos in enumerate(hinge_positions, start=1):
                hw_builder.add_hinge(
                    f"{name}_Hinge_{idx}",
                    (hx, hy, pz + pos),
                    hw_group
                )
