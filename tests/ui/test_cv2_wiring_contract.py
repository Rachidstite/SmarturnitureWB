import ast
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


REPO_ROOT = Path(__file__).resolve().parents[2]

CV2_PACKAGE = REPO_ROOT / "ui" / "configurator_v2"

CONFIGURATOR_V2_MODULES = tuple(
    str(p.relative_to(REPO_ROOT)).replace("/", ".").replace(".py", "")
    for p in CV2_PACKAGE.rglob("*.py")
    if p.name != "__init__.py"
    and "__pycache__" not in str(p)
)

FORBIDDEN_FREECAD_IMPORTS = {
    "FreeCAD",
    "FreeCADGui",
    "Part",
}


def _fake_freecad_gui():
    """Create a minimal FreeCADGui mock that supports addCommand and addWorkbench."""
    workbench_cls = type("Workbench", (), {
        "Initialize": lambda self: None,
        "GetClassName": lambda self: "Gui::PythonWorkbench",
    })
    return types.SimpleNamespace(
        listCommands=lambda: [],
        addCommand=lambda name, cmd: None,
        addWorkbench=lambda wb: None,
        Workbench=workbench_cls,
    )


def _patch_freecad_gui():
    """Return a dict suitable for patch.dict(sys.modules) to fake FreeCADGui."""
    return {"FreeCADGui": _fake_freecad_gui()}


class TestCv2CommandExistence(unittest.TestCase):
    """Tests that both the legacy and new commands exist and are structurally correct."""

    def _import_module(self):
        """Import commands.workbench_commands with FreeCADGui mocked."""
        with patch.dict(sys.modules, _patch_freecad_gui()):
            import commands.workbench_commands
            return commands.workbench_commands

    def test_open_configurator_command_exists(self):
        """OpenConfiguratorCommand must still be importable."""
        mod = self._import_module()
        self.assertTrue(hasattr(mod, "OpenConfiguratorCommand"))

    def test_open_configurator_command_opens_legacy_ui_manager(self):
        """OpenConfiguratorCommand.Activated must reference UIManager."""
        source_path = REPO_ROOT / "commands" / "workbench_commands.py"
        source = source_path.read_text()
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "OpenConfiguratorCommand":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "Activated":
                        segment = ast.get_source_segment(source, item)
                        self.assertIn("UIManager", segment)
                        found = True
                        break
                break
        self.assertTrue(found, "OpenConfiguratorCommand.Activated must reference UIManager")

    def test_open_configurator_v2_command_exists(self):
        """OpenConfiguratorV2Command must be importable."""
        mod = self._import_module()
        self.assertTrue(hasattr(mod, "OpenConfiguratorV2Command"))

    def test_open_configurator_v2_helper_exists(self):
        """_open_configurator_v2 helper must be importable."""
        mod = self._import_module()
        self.assertTrue(hasattr(mod, "_open_configurator_v2"))


class TestInitGuiRegistration(unittest.TestCase):
    """Tests that InitGui.py registers both commands correctly."""

    def _import_init_gui(self):
        with patch.dict(sys.modules, _patch_freecad_gui()):
            import InitGui
            return InitGui

    def test_init_gui_registers_open_configurator(self):
        """InitGui must register SmartFurniture_OpenConfigurator."""
        source_path = REPO_ROOT / "InitGui.py"
        source = source_path.read_text()
        self.assertIn("SmartFurniture_OpenConfigurator", source)

    def test_init_gui_registers_open_configurator_v2(self):
        """InitGui must register SmartFurniture_OpenConfiguratorV2."""
        source_path = REPO_ROOT / "InitGui.py"
        source = source_path.read_text()
        self.assertIn("SmartFurniture_OpenConfiguratorV2", source)
        self.assertIn("OpenConfiguratorV2Command", source)

    def test_init_gui_adds_both_to_toolbar_and_menu(self):
        """Both commands must appear in toolbar and menu lists."""
        source_path = REPO_ROOT / "InitGui.py"
        source = source_path.read_text()
        c1 = source.count("SmartFurniture_OpenConfigurator")
        c2 = source.count("SmartFurniture_OpenConfiguratorV2")
        self.assertGreaterEqual(c1, 2)
        self.assertGreaterEqual(c2, 2)


class TestCv2WiringLogic(unittest.TestCase):
    """Tests that _open_configurator_v2 wires services correctly using lazy imports."""

    def _call_helper_with_mocks(self):
        """Call _open_configurator_v2 with all its lazy imports mocked.

        We mock at the *import target* (the actual CV2/ui package functions)
        rather than trying to patch names inside the commands module, because
        the imports are lazy (inside the function body).

        Also patches core.qt_compat to prevent PySide6 crash when
        ui.configurator_v2.workspace is imported.
        """
        mock_workspace = Mock()
        mock_integration = Mock()
        mock_integration.create_base_cabinet = Mock(return_value=Mock())
        mock_eng_service = Mock()
        mock_eng_service.execute.return_value = Mock()

        qt_mock = types.SimpleNamespace(
            QtWidgets=types.SimpleNamespace(
                QWidget=Mock, QFrame=Mock, QVBoxLayout=Mock,
                QHBoxLayout=Mock, QFormLayout=Mock, QComboBox=Mock,
                QPushButton=Mock, QLabel=Mock, QTabWidget=Mock,
                QLineEdit=Mock, QGraphicsView=Mock, QGraphicsScene=Mock,
            ),
            QtCore=types.SimpleNamespace(),
        )

        module_patches = {
            "FreeCADGui": _fake_freecad_gui(),
            "core.qt_compat": qt_mock,
            "PySide6": Mock(),
            "PySide6.QtWidgets": Mock(),
            "shiboken6": Mock(),
            # Pre-cache mock modules for lazy imports inside _open_configurator_v2
            # so they are never resolved from a real, already-cached module
            "application": Mock(),
            "application.engineering_application_service": Mock(
                EngineeringApplicationService=Mock(return_value=mock_eng_service),
            ),
            "application.base_application_service": Mock(),
            "application.application_service_result": Mock(),
        }

        with patch.dict(sys.modules, module_patches):
            from commands.workbench_commands import _open_configurator_v2

            with patch("ui.configurator_v2.create_configurator_v2_workspace",
                       return_value=mock_workspace) as mock_create:
                with patch("ui.configurator_v2.ConfiguratorV2ServiceBindings",
                           return_value=Mock()) as mock_bindings:
                    with patch("ui.configurator_v2.service_integration.attach_service_integration",
                               return_value=mock_integration) as mock_attach:
                        result = _open_configurator_v2()

        return {
            "workspace": mock_workspace,
            "integration": mock_integration,
            "eng_service": mock_eng_service,
            "bindings_cls": mock_bindings,
            "create_workspace": mock_create,
            "attach": mock_attach,
            "result": result,
        }

    def test_helper_creates_service_bindings_with_engineering_service(self):
        mocks = self._call_helper_with_mocks()
        # EngineeringApplicationService is in sys.modules mock;
        # verify it was called (instantiated) and passed to ConfiguratorV2ServiceBindings
        mocks["bindings_cls"].assert_called_once()
        call_kwargs = mocks["bindings_cls"].call_args.kwargs
        self.assertIn("engineering_application_service", call_kwargs)
        self.assertIsNotNone(call_kwargs["engineering_application_service"])

    def test_helper_calls_attach_service_integration(self):
        mocks = self._call_helper_with_mocks()
        mocks["attach"].assert_called_once()

    def test_helper_shows_workspace(self):
        mocks = self._call_helper_with_mocks()
        mocks["workspace"].show.assert_called_once()

    def test_helper_returns_workspace(self):
        mocks = self._call_helper_with_mocks()
        self.assertIs(mocks["result"], mocks["workspace"])

    def test_helper_creates_base_cabinet(self):
        mocks = self._call_helper_with_mocks()
        mocks["integration"].create_base_cabinet.assert_called_once()

    def test_helper_sets_project_context(self):
        mocks = self._call_helper_with_mocks()
        mocks["workspace"].set_project_context.assert_called_once_with(
            current_product_family="Base Cabinet",
        )

    def test_open_configurator_v2_command_calls_helper(self):
        """OpenConfiguratorV2Command.Activated must reference _open_configurator_v2."""
        source_path = REPO_ROOT / "commands" / "workbench_commands.py"
        source = source_path.read_text()
        tree = ast.parse(source)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "OpenConfiguratorV2Command":
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "Activated":
                        segment = ast.get_source_segment(source, item)
                        self.assertIn("_open_configurator_v2", segment)
                        found = True
                        break
                break
        self.assertTrue(found, "Activated must call _open_configurator_v2")


class TestCv2NoFreeCADImports(unittest.TestCase):
    """Architecture tests — ui/configurator_v2 must not import FreeCAD."""

    def test_no_configurator_v2_module_imports_freecad(self):
        for module_path_str in CONFIGURATOR_V2_MODULES:
            rel = module_path_str.replace(".", "/")
            file_path = REPO_ROOT / f"{rel}.py"
            if not file_path.exists():
                continue
            tree = ast.parse(file_path.read_text())
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = []
                    if isinstance(node, ast.Import):
                        names = [alias.name for alias in node.names]
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            names = [node.module]
                            names += [alias.name for alias in node.names]
                    for name in names:
                        top = name.split(".")[0]
                        self.assertNotIn(
                            top, FORBIDDEN_FREECAD_IMPORTS,
                            f"{module_path_str} imports {top} (forbidden)",
                        )

    def test_commands_workbench_imports_freecad_gui(self):
        source_path = REPO_ROOT / "commands" / "workbench_commands.py"
        source = source_path.read_text()
        tree = ast.parse(source)
        has_freecad = any(
            isinstance(node, ast.Import)
            and any(alias.name == "FreeCADGui" for alias in node.names)
            for node in ast.walk(tree)
        )
        self.assertTrue(has_freecad, "commands/workbench_commands.py must import FreeCADGui")


if __name__ == "__main__":
    unittest.main()
