import FreeCADGui
from commands.workbench_commands import OpenConfiguratorCommand, CreateWardrobeCommand

if "SmartFurniture_OpenConfigurator" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_OpenConfigurator", OpenConfiguratorCommand())

if "SmartFurniture_CreateWardrobe" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_CreateWardrobe", CreateWardrobeCommand())

class SmartFurnitureWorkbench(FreeCADGui.Workbench):
    MenuText = "Smart Furniture"
    ToolTip = "Professional MDF CNC Design Platform"
    Icon = ""
    def Initialize(self):
        self.appendToolbar("SmartFurniture", ["SmartFurniture_OpenConfigurator", "SmartFurniture_CreateWardrobe"])
        self.appendMenu("Smart Furniture", ["SmartFurniture_OpenConfigurator", "SmartFurniture_CreateWardrobe"])
    def GetClassName(self): return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(SmartFurnitureWorkbench())

print("### SMARTFURNITURE V1-1 LOADED ###")
print("### V1-1 VERSION LOADED ###")
