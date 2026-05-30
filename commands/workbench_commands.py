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
