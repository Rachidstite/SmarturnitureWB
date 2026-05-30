import FreeCAD as App, Part
class CNCBuilder:
    def __init__(self, mat): self.mat = mat
    def drill_hinge_cup(self, door_shape, door_h):
        t = self.mat.mdf_thickness; r = self.mat.hinge_cup_dia / 2; depth = self.mat.hinge_cup_depth
        c1 = Part.makeCylinder(r, depth + 1, App.Vector(22.5, t + 0.5, 100), App.Vector(0, -1, 0))
        c2 = Part.makeCylinder(r, depth + 1, App.Vector(22.5, t + 0.5, door_h - 100), App.Vector(0, -1, 0))
        return door_shape.cut(Part.makeCompound([c1, c2]))
    def generate_side_screw_holes(self, side_shape, shelves_z, D, sliding_space=0, is_left=True):
        t = self.mat.mdf_thickness; r = self.mat.minifix_pin_dia / 2; depth = self.mat.minifix_pin_depth
        tools = []
        for z in shelves_z:
            y_f = sliding_space + 50; y_b = D - 70
            if is_left:
                tools.append(Part.makeCylinder(r, depth, App.Vector(t, y_f, z + t / 2), App.Vector(-1, 0, 0)))
                tools.append(Part.makeCylinder(r, depth, App.Vector(t, y_b, z + t / 2), App.Vector(-1, 0, 0)))
            else:
                tools.append(Part.makeCylinder(r, depth, App.Vector(0, y_f, z + t / 2), App.Vector(1, 0, 0)))
                tools.append(Part.makeCylinder(r, depth, App.Vector(0, y_b, z + t / 2), App.Vector(1, 0, 0)))
        if not tools: return side_shape
        return side_shape.cut(Part.makeCompound(tools))
