import FreeCAD as App, Part
class DrawerBuilder:
    @staticmethod
    def build(doc, parent_group, name, fw, fh, fx, fy, fz, bw, bh, bd, bpx, bpy, bpz, mat, bottom_t):
        grp = doc.addObject("App::DocumentObjectGroup", name); parent_group.addObject(grp)
        face = doc.addObject("Part::Feature", f"{name}_Face")
        face.Shape = Part.makeBox(fw, mat.mdf_thickness, fh)
        face.Placement = App.Placement(App.Vector(fx, fy, fz), App.Rotation()); face.ViewObject.ShapeColor = (
        0.9, 0.8, 0.7); grp.addObject(face)
        box_t = mat.mdf_thickness
        def add_part(pname, pw, pd, ph, px, py, pz, color=(0.95, 0.95, 0.95)):
            p = doc.addObject("Part::Feature", pname); p.Shape = Part.makeBox(pw, pd, ph)
            p.Placement = App.Placement(App.Vector(px, py, pz), App.Rotation()); p.ViewObject.ShapeColor = color; grp.addObject(p)
        add_part(f"{name}_Side_L", box_t, bd, bh, bpx, bpy, bpz)
        add_part(f"{name}_Side_R", box_t, bd, bh, bpx + bw - box_t, bpy, bpz)
        iw = bw - 2 * box_t
        add_part(f"{name}_Box_Front", iw, box_t, bh, bpx + box_t, bpy, bpz)
        add_part(f"{name}_Box_Back", iw, box_t, bh, bpx + box_t, bpy + bd - box_t, bpz)
        btw = bw - 2 * box_t; btd = bd - 2 * box_t
        add_part(f"{name}_Bottom", btw, btd, bottom_t, bpx + box_t, bpy + box_t, bpz + mat.drawer_bottom_inset,
                 (0.8, 0.8, 0.8))
