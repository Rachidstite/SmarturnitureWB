import FreeCADGui
class OpenConfiguratorCommand:
    def GetResources(self): return {'Pixmap': '', 'MenuText': 'Configurator', 'ToolTip': 'Open Pro Dressing Configurator'}
    def Activated(self):
        from ui.main_window import UIManager
        global dressing_app
        try: dressing_app.close()
        except: pass
        dressing_app = UIManager(); dressing_app.show()
    def IsActive(self): return True

class CreateWardrobeCommand:
    def GetResources(self):
        return {
            'Pixmap': '',
            'MenuText': 'Create Wardrobe',
            'ToolTip': 'Create demo wardrobe and render it'
        }

    def Activated(self):
        from domain.builders import WardrobeBuilder
        from gui.renderer import GeometryRenderer

        cab = WardrobeBuilder(
            uid="DEMO",
            width=1200,
            height=2400,
            depth=600
        )

        cab.add_divider(600)

        project = cab.build()

        GeometryRenderer.render(project)

    def IsActive(self):
        return True
