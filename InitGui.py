import FreeCADGui
from commands.workbench_commands import (
    OpenConfiguratorCommand,
    CreateEngineeringDemonstrationCommand,
    CreateWardrobeCommand,
    OpenConfiguratorV2Command,
)

if "SmartFurniture_OpenConfigurator" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_OpenConfigurator", OpenConfiguratorCommand())

if "SmartFurniture_OpenConfiguratorV2" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_OpenConfiguratorV2", OpenConfiguratorV2Command())

if "SmartFurniture_CreateWardrobe" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand("SmartFurniture_CreateWardrobe", CreateWardrobeCommand())

if "SmartFurniture_EngineeringDemo" not in FreeCADGui.listCommands():
    FreeCADGui.addCommand(
        "SmartFurniture_EngineeringDemo",
        CreateEngineeringDemonstrationCommand(),
    )

class SmartFurnitureWorkbench(FreeCADGui.Workbench):
    MenuText = "Smart Furniture"
    ToolTip = "Professional MDF CNC Design Platform"
    Icon = ""
    def Initialize(self):
        self.appendToolbar(
            "SmartFurniture",
            [
                "SmartFurniture_OpenConfigurator",
                "SmartFurniture_OpenConfiguratorV2",
                "SmartFurniture_CreateWardrobe",
                "SmartFurniture_EngineeringDemo",
            ],
        )
        self.appendMenu(
            "Smart Furniture",
            [
                "SmartFurniture_OpenConfigurator",
                "SmartFurniture_OpenConfiguratorV2",
                "SmartFurniture_CreateWardrobe",
                "SmartFurniture_EngineeringDemo",
            ],
        )
    def GetClassName(self): return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(SmartFurnitureWorkbench())

print("### SMARTFURNITURE V1-1 LOADED ###")
print("### V1-1 VERSION LOADED ###")
