import FreeCADGui
from commands.workbench_commands import OpenConfiguratorCommand

if "SmartFurniture_OpenConfigurator" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_OpenConfigurator", OpenConfiguratorCommand())

class SmartFurnitureWorkbench(FreeCADGui.Workbench):
    MenuText = "Smart Furniture"
    ToolTip = "Professional MDF CNC Design Platform"
    Icon = ""
    def Initialize(self):
        self.appendToolbar("SmartFurniture", ["SmartFurniture_OpenConfigurator"])
        self.appendMenu("Smart Furniture", ["SmartFurniture_OpenConfigurator"])
    def GetClassName(self): return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(SmartFurnitureWorkbench())
