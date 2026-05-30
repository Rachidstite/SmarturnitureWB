import FreeCAD as App, Part
class HardwareBuilder:
    def __init__(self, doc): self.doc = doc
    def add_minifix(self, name, pos, group):
        cam = self.doc.addObject("Part::Feature", name); cam.Shape = Part.makeCylinder(7.5, 12)
        cam.Placement = App.Placement(App.Vector(pos[0], pos[1], pos[2] - 0.5), App.Rotation()); cam.ViewObject.ShapeColor = (0.95, 0.95, 0.95); group.addObject(cam)
    def add_hinge(self, name, pos, group):
        hinge = self.doc.addObject("Part::Feature", name); hinge.Shape = Part.makeCylinder(17.5, 13)
        hinge.Placement = App.Placement(App.Vector(*pos), App.Rotation(App.Vector(1, 0, 0), -90)); hinge.ViewObject.ShapeColor = (0.95, 0.95, 0.95); group.addObject(hinge)
