import importlib
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from shared.contracts import CabinetParams


class _FakeSpinBox:
    def __init__(self, value):
        self._value = float(value)
        self._pending_value = None

    def value(self):
        return self._value

    def setValue(self, value):
        self._value = float(value)
        self._pending_value = None

    def setPendingValue(self, value):
        self._pending_value = float(value)

    def interpretText(self):
        if self._pending_value is not None:
            self._value = self._pending_value
            self._pending_value = None


def _configure_section_width_manager(manager, section_widths, width=1800.0):
    manager.params = CabinetParams(width=width, sec_count=3, section_widths=list(section_widths))
    manager.section_width_inputs = [_FakeSpinBox(value) for value in section_widths]
    manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
    manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
    manager.btn_build = SimpleNamespace(setEnabled=Mock())
    manager.build_timer = _FakeTimer()
    manager.issue_presenter = SimpleNamespace(display_issues=Mock())
    manager.builder = SimpleNamespace(build=Mock(), mat=SimpleNamespace())
    manager.val_state = SimpleNamespace(has_errors=False, issues=())
    manager.is_updating_ui = False
    manager.inp_w = SimpleNamespace(value=lambda: width)
    manager.inp_h = SimpleNamespace(value=lambda: 2200.0)
    manager.inp_d = SimpleNamespace(value=lambda: 600.0)
    manager.inp_base = SimpleNamespace(value=lambda: 80.0)
    manager.inp_back_thickness = SimpleNamespace(value=lambda: 8.0)
    manager.inp_drawer_depth = SimpleNamespace(value=lambda: 450.0)
    manager.inp_drawer_bottom = SimpleNamespace(value=lambda: 8.0)
    manager.inp_sec = SimpleNamespace(value=lambda: 3)
    manager.chk_cnc = SimpleNamespace(isChecked=lambda: False)
    manager.chk_hw = SimpleNamespace(isChecked=lambda: False)
    manager.cmb_hinge = SimpleNamespace(currentData=lambda: "HINGE_BLUM_110_V1")
    manager.cmb_slide = SimpleNamespace(currentData=lambda: "DRAWER_SLIDE_SOFTCLOSE_450")
    manager.cmb_handle = SimpleNamespace(currentData=lambda: "HANDLE_128_BLACK")


class _FakeTimer:
    def __init__(self):
        self.start_calls = 0
        self.stop_calls = 0
        self.last_interval = None

    def start(self, interval):
        self.start_calls += 1
        self.last_interval = interval

    def stop(self):
        self.stop_calls += 1


def _fake_qt_compat_module():
    fake_qt_widgets = types.SimpleNamespace(
        QMainWindow=type("QMainWindow", (), {}),
        QWidget=type("QWidget", (), {}),
        QVBoxLayout=type("QVBoxLayout", (), {}),
        QTabWidget=type("QTabWidget", (), {}),
        QCheckBox=type("QCheckBox", (), {}),
        QPushButton=type("QPushButton", (), {}),
        QLabel=type("QLabel", (), {}),
        QFormLayout=type("QFormLayout", (), {}),
        QDoubleSpinBox=type("QDoubleSpinBox", (), {}),
        QSpinBox=type("QSpinBox", (), {}),
        QComboBox=type("QComboBox", (), {}),
        QMessageBox=type("QMessageBox", (), {}),
        QFileDialog=type("QFileDialog", (), {}),
    )
    fake_qt_core = types.SimpleNamespace(QTimer=type("QTimer", (), {}))
    return types.SimpleNamespace(QtWidgets=fake_qt_widgets, QtCore=fake_qt_core)


def _import_ui_main_window():
    fake_qt_module = _fake_qt_compat_module()
    fake_freecad = types.ModuleType("FreeCAD")
    fake_part = types.ModuleType("Part")
    fake_freecad_gui = types.ModuleType("FreeCADGui")
    fake_freecad_gui.listCommands = lambda: []
    fake_freecad_gui.addCommand = lambda *args, **kwargs: None
    fake_freecad_gui.addWorkbench = lambda *args, **kwargs: None
    with patch.dict(
        sys.modules,
        {
            "core.qt_compat": fake_qt_module,
            "FreeCAD": fake_freecad,
            "Part": fake_part,
            "FreeCADGui": fake_freecad_gui,
        },
    ):
        module = importlib.import_module("ui.main_window")
    return module


class TestConfiguratorPipelineContract(unittest.TestCase):
    def test_configurator_build_returns_to_legacy_visible_cabinet_path(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        legacy_scene_graph = object()
        legacy_cabinet = SimpleNamespace(scene_graph=legacy_scene_graph)

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(
            width=800.0,
            height=720.0,
            depth=560.0,
            base_height=80.0,
            sec_count=1,
            sec_data={0: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="None", door_count=2)},
            hinge_sku="HINGE_BLUM_110_V1",
        )
        manager.builder = SimpleNamespace(mat=SimpleNamespace(), scene_graph=None)
        manager.builder.build = Mock(
            side_effect=lambda cabinet: setattr(
                manager.builder,
                "scene_graph",
                legacy_scene_graph,
            )
        )
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())

        validation_state = SimpleNamespace(has_errors=False, issues=())

        # Architecture debt: legacy validation still runs before the legacy visible cabinet build.
        # Keep this mixed path narrow; do not expand it into new construction logic.
        with patch.object(
            main_window_module,
            "ValidationService",
        ) as validation_service_cls:
            validation_service_cls.return_value.validate_only.return_value = validation_state

            manager.trigger_build()

        validation_service_cls.assert_called_once()
        validation_service_cls.return_value.validate_only.assert_called_once()
        manager.builder.build.assert_called_once()
        built_cabinet = manager.builder.build.call_args.args[0]
        self.assertIs(built_cabinet.params, manager.params)
        self.assertIsNotNone(getattr(built_cabinet, "construction_model", None))
        self.assertIsNotNone(getattr(built_cabinet, "engineering_model", None))
        self.assertIs(manager.builder.scene_graph, legacy_scene_graph)

    def test_configurator_build_uses_engineering_entry_plumbing(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(
            width=1800.0,
            height=2200.0,
            depth=600.0,
            base_height=80.0,
            sec_count=3,
            section_widths=[450.0, 900.0, 450.0],
            sec_data={
                0: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="None", door_count=2),
                1: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="None", door_count=2),
                2: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="None", door_count=2),
            },
        )
        manager.builder = SimpleNamespace(
            mat=SimpleNamespace(),
            build=Mock(return_value=SimpleNamespace(scene_graph=object())),
            scene_graph=None,
        )
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())
        manager.build_timer = _FakeTimer()
        manager.inp_w = SimpleNamespace(value=lambda: 1800.0)
        manager.inp_h = SimpleNamespace(value=lambda: 2200.0)
        manager.inp_d = SimpleNamespace(value=lambda: 600.0)
        manager.inp_base = SimpleNamespace(value=lambda: 80.0)
        manager.inp_back_thickness = SimpleNamespace(value=lambda: 8.0)
        manager.inp_drawer_depth = SimpleNamespace(value=lambda: 450.0)
        manager.inp_drawer_bottom = SimpleNamespace(value=lambda: 8.0)
        manager.inp_sec = SimpleNamespace(value=lambda: 3)
        manager.chk_cnc = SimpleNamespace(isChecked=lambda: False)
        manager.chk_hw = SimpleNamespace(isChecked=lambda: False)
        manager.cmb_hinge = SimpleNamespace(currentData=lambda: "HINGE_BLUM_110_V1")
        manager.cmb_slide = SimpleNamespace(currentData=lambda: "DRAWER_SLIDE_SOFTCLOSE_450")
        manager.cmb_handle = SimpleNamespace(currentData=lambda: "HANDLE_128_BLACK")

        validation_state = SimpleNamespace(has_errors=False, issues=())

        with patch.object(
            main_window_module,
            "ValidationService",
        ) as validation_service_cls:
            validation_service_cls.return_value.validate_only.return_value = validation_state

            manager.trigger_build()

        validation_service_cls.assert_called_once()
        manager.builder.build.assert_called_once()
        built_cabinet = manager.builder.build.call_args.args[0]
        self.assertIsNotNone(getattr(built_cabinet, "construction_model", None))
        self.assertIsNotNone(getattr(built_cabinet, "engineering_model", None))
        self.assertEqual(built_cabinet.params.section_widths, [450.0, 900.0, 450.0])

    def test_default_section_widths_are_equal(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3)

        self.assertEqual(manager._default_section_widths(), [600.0, 600.0, 600.0])

    def test_section_count_change_resets_equal_widths(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3)
        manager.section_width_inputs = [_FakeSpinBox(450.0), _FakeSpinBox(900.0), _FakeSpinBox(450.0)]
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())
        manager._last_cabinet_width = 1800.0

        manager._rebalance_section_widths_for_count_change()

        self.assertEqual(manager.params.section_widths, [600.0, 600.0, 600.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [600.0, 600.0, 600.0])
        manager.lbl_section_width_status.setText.assert_called()

    def test_cabinet_width_change_keeps_equal_distribution_equal(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3, section_widths=[600.0, 600.0, 600.0])
        manager.section_width_inputs = [_FakeSpinBox(600.0), _FakeSpinBox(600.0), _FakeSpinBox(600.0)]
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())

        manager._rebalance_section_widths_for_width_change(1800.0, 2100.0)

        self.assertEqual(manager.params.section_widths, [700.0, 700.0, 700.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [700.0, 700.0, 700.0])

    def test_cabinet_width_change_preserves_unequal_ratios(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3, section_widths=[450.0, 900.0, 450.0])
        manager.section_width_inputs = [_FakeSpinBox(450.0), _FakeSpinBox(900.0), _FakeSpinBox(450.0)]
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())

        manager._rebalance_section_widths_for_width_change(1800.0, 2400.0)

        self.assertEqual(manager.params.section_widths, [600.0, 1200.0, 600.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [600.0, 1200.0, 600.0])

    def test_equalize_button_sets_equal_widths(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3, section_widths=[450.0, 900.0, 450.0])
        manager.section_width_inputs = [_FakeSpinBox(450.0), _FakeSpinBox(900.0), _FakeSpinBox(450.0)]
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())
        manager.on_param_changed = Mock()

        manager.equalize_sections()

        self.assertEqual(manager.params.section_widths, [600.0, 600.0, 600.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [600.0, 600.0, 600.0])
        manager.on_param_changed.assert_called_once()

    def test_manual_widget_values_survive_on_param_changed(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        _configure_section_width_manager(manager, [450.0, 900.0, 450.0])
        for spin, value in zip(manager.section_width_inputs, [450.0, 900.0, 450.0]):
            spin.setPendingValue(value)

        manager.on_param_changed()

        self.assertEqual(manager.params.section_widths, [450.0, 900.0, 450.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [450.0, 900.0, 450.0])
        self.assertEqual(manager.build_timer.start_calls, 1)

    def test_trigger_build_attaches_engineering_models_before_builder_call(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        _configure_section_width_manager(manager, [450.0, 900.0, 450.0])
        validation_state = SimpleNamespace(has_errors=False, issues=())

        with patch.object(
            main_window_module,
            "ValidationService",
        ) as validation_service_cls:
            validation_service_cls.return_value.validate_only.return_value = validation_state

            manager.trigger_build()

        manager.builder.build.assert_called_once()
        built_cabinet = manager.builder.build.call_args.args[0]
        self.assertIsNotNone(getattr(built_cabinet, "construction_model", None))
        self.assertIsNotNone(getattr(built_cabinet, "engineering_model", None))

    def test_on_section_width_changed_preserves_manual_values(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager
        manager = UIManager.__new__(UIManager)
        _configure_section_width_manager(manager, [600.0, 600.0, 600.0])
        for spin, value in zip(manager.section_width_inputs, [450.0, 900.0, 450.0]):
            spin.setPendingValue(value)

        manager.on_section_width_changed()

        self.assertEqual(manager.params.section_widths, [450.0, 900.0, 450.0])
        self.assertEqual([spin.value() for spin in manager.section_width_inputs], [450.0, 900.0, 450.0])
        self.assertEqual(manager.build_timer.start_calls, 1)

    def test_trigger_build_uses_widget_section_widths(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        _configure_section_width_manager(manager, [600.0, 600.0, 600.0])
        for spin, value in zip(manager.section_width_inputs, [450.0, 900.0, 450.0]):
            spin.setPendingValue(value)

        validation_state = SimpleNamespace(has_errors=False, issues=())

        with patch.object(main_window_module, "ValidationService") as validation_service_cls, patch.object(
            main_window_module,
            "Cabinet",
            side_effect=lambda params: SimpleNamespace(params=params),
        ) as cabinet_cls:
            validation_service_cls.return_value.validate_only.return_value = validation_state

            manager.trigger_build()

        cabinet_cls.assert_called_once()
        built_params = cabinet_cls.call_args.args[0]
        self.assertEqual(built_params.section_widths, [450.0, 900.0, 450.0])

    def test_invalid_section_widths_block_configurator_build(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(
            width=1800.0,
            height=2200.0,
            depth=600.0,
            base_height=80.0,
            sec_count=3,
            sec_data={
                0: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                1: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                2: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
            },
            section_widths=[450.0, 800.0, 450.0],
        )
        manager.builder = SimpleNamespace(
            mat=SimpleNamespace(),
            build=Mock(),
            scene_graph=None,
        )
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())

        with patch.object(
            main_window_module,
            "ValidationService",
        ) as validation_service_cls:
            manager.trigger_build()

        validation_service_cls.assert_not_called()
        manager.builder.build.assert_not_called()
        self.assertTrue(manager.val_state.has_errors)
        manager.issue_presenter.display_issues.assert_called_once()
        self.assertTrue(any(issue.code == "SECTION_WIDTH_TOTAL_MISMATCH" for issue in manager.val_state.issues))

    def test_invalid_intermediate_section_widths_do_not_start_build_timer(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(
            width=1800.0,
            height=2200.0,
            depth=600.0,
            base_height=80.0,
            sec_count=3,
            sec_data={
                0: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                1: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                2: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
            },
            section_widths=[450.0, 800.0, 450.0],
        )
        manager.section_width_inputs = [_FakeSpinBox(450.0), _FakeSpinBox(800.0), _FakeSpinBox(450.0)]
        manager.btn_build = SimpleNamespace(setEnabled=Mock())
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.build_timer = _FakeTimer()
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())
        manager.builder = SimpleNamespace(build=Mock(), mat=SimpleNamespace())
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.inp_w = SimpleNamespace(value=lambda: 1800.0)
        manager.inp_h = SimpleNamespace(value=lambda: 2200.0)
        manager.inp_d = SimpleNamespace(value=lambda: 600.0)
        manager.inp_base = SimpleNamespace(value=lambda: 80.0)
        manager.inp_back_thickness = SimpleNamespace(value=lambda: 8.0)
        manager.inp_drawer_depth = SimpleNamespace(value=lambda: 450.0)
        manager.inp_drawer_bottom = SimpleNamespace(value=lambda: 8.0)
        manager.inp_sec = SimpleNamespace(value=lambda: 3)
        manager.chk_cnc = SimpleNamespace(isChecked=lambda: False)
        manager.chk_hw = SimpleNamespace(isChecked=lambda: False)
        manager.cmb_hinge = SimpleNamespace(currentData=lambda: "HINGE_BLUM_110_V1")
        manager.cmb_slide = SimpleNamespace(currentData=lambda: "DRAWER_SLIDE_SOFTCLOSE_450")
        manager.cmb_handle = SimpleNamespace(currentData=lambda: "HANDLE_128_BLACK")

        manager.on_param_changed()

        self.assertEqual(manager.build_timer.start_calls, 0)
        self.assertGreaterEqual(manager.build_timer.stop_calls, 1)
        manager.builder.build.assert_not_called()
        self.assertFalse(manager.btn_build.setEnabled.call_args.args[0])

    def test_width_edit_does_not_rebuild_section_width_inputs(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(
            width=1800.0,
            height=2200.0,
            depth=600.0,
            base_height=80.0,
            sec_count=3,
            sec_data={
                0: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                1: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
                2: SimpleNamespace(drawers=0, drawer_type="Inset", shelves=1, doors="Inset", door_count=1),
            },
            section_widths=[450.0, 900.0, 450.0],
        )
        manager.section_width_inputs = [_FakeSpinBox(450.0), _FakeSpinBox(900.0), _FakeSpinBox(450.0)]
        manager._rebuild_section_width_inputs = Mock()
        manager._last_cabinet_width = 1800.0
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.btn_build = SimpleNamespace(setEnabled=Mock())
        manager.build_timer = _FakeTimer()
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())
        manager.builder = SimpleNamespace(build=Mock(), mat=SimpleNamespace())
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.inp_w = SimpleNamespace(value=lambda: 2100.0)
        manager.inp_h = SimpleNamespace(value=lambda: 2200.0)
        manager.inp_d = SimpleNamespace(value=lambda: 600.0)
        manager.inp_base = SimpleNamespace(value=lambda: 80.0)
        manager.inp_back_thickness = SimpleNamespace(value=lambda: 8.0)
        manager.inp_drawer_depth = SimpleNamespace(value=lambda: 450.0)
        manager.inp_drawer_bottom = SimpleNamespace(value=lambda: 8.0)
        manager.inp_sec = SimpleNamespace(value=lambda: 3)
        manager.chk_cnc = SimpleNamespace(isChecked=lambda: False)
        manager.chk_hw = SimpleNamespace(isChecked=lambda: False)
        manager.cmb_hinge = SimpleNamespace(currentData=lambda: "HINGE_BLUM_110_V1")
        manager.cmb_slide = SimpleNamespace(currentData=lambda: "DRAWER_SLIDE_SOFTCLOSE_450")
        manager.cmb_handle = SimpleNamespace(currentData=lambda: "HANDLE_128_BLACK")

        manager.on_param_changed()

        manager._rebuild_section_width_inputs.assert_not_called()

    def test_valid_section_widths_start_build_timer_once(self):
        main_window_module = _import_ui_main_window()
        UIManager = main_window_module.UIManager

        manager = UIManager.__new__(UIManager)
        manager.params = CabinetParams(width=1800.0, sec_count=3, section_widths=[600.0, 600.0, 600.0])
        manager.section_width_inputs = [_FakeSpinBox(600.0), _FakeSpinBox(600.0), _FakeSpinBox(600.0)]
        manager.btn_build = SimpleNamespace(setEnabled=Mock())
        manager.lbl_section_width_total = SimpleNamespace(setText=Mock())
        manager.lbl_section_width_status = SimpleNamespace(setText=Mock())
        manager.build_timer = _FakeTimer()
        manager.issue_presenter = SimpleNamespace(display_issues=Mock())
        manager.builder = SimpleNamespace(build=Mock(), mat=SimpleNamespace())
        manager.val_state = SimpleNamespace(has_errors=False, issues=())
        manager.is_updating_ui = False
        manager.inp_w = SimpleNamespace(value=lambda: 1800.0)
        manager.inp_h = SimpleNamespace(value=lambda: 2200.0)
        manager.inp_d = SimpleNamespace(value=lambda: 600.0)
        manager.inp_base = SimpleNamespace(value=lambda: 80.0)
        manager.inp_back_thickness = SimpleNamespace(value=lambda: 8.0)
        manager.inp_drawer_depth = SimpleNamespace(value=lambda: 450.0)
        manager.inp_drawer_bottom = SimpleNamespace(value=lambda: 8.0)
        manager.inp_sec = SimpleNamespace(value=lambda: 3)
        manager.chk_cnc = SimpleNamespace(isChecked=lambda: False)
        manager.chk_hw = SimpleNamespace(isChecked=lambda: False)
        manager.cmb_hinge = SimpleNamespace(currentData=lambda: "HINGE_BLUM_110_V1")
        manager.cmb_slide = SimpleNamespace(currentData=lambda: "DRAWER_SLIDE_SOFTCLOSE_450")
        manager.cmb_handle = SimpleNamespace(currentData=lambda: "HANDLE_128_BLACK")

        manager.on_param_changed()

        self.assertEqual(manager.build_timer.start_calls, 1)
        self.assertEqual(manager.build_timer.last_interval, 300)
        self.assertEqual(manager.build_timer.stop_calls, 0)


if __name__ == "__main__":
    unittest.main()
