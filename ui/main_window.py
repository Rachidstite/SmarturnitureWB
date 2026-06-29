from core.qt_compat import QtWidgets, QtCore
from shared.contracts import CabinetParams, SectionConfig; from shared.enums import DrawerLayoutMode
from shared.issues import ValidationState, GeometryIssue; from shared.enums import Domain
from core.logging_config import logger
from engine.cabinet import Cabinet; from engine.cabinet_builder import CabinetBuilder
from domain.base_cabinet_specification_adapter import BaseCabinetSpecificationAdapter
from domain.base_cabinet_engineering_entry import attach_base_cabinet_engineering_models
from services.validation_service import ValidationService; from ui.issue_presenter import IssuePresenter
import csv
from costing.cost_engine import CostEngine

class UIManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(); self.params = CabinetParams(); self.builder = CabinetBuilder(); self.val_state = ValidationState()
        self.is_updating_ui = False; self.section_width_inputs = []; self._last_cabinet_width = self.params.width; self.build_timer = QtCore.QTimer(); self.build_timer.setSingleShot(True); self.build_timer.timeout.connect(self.trigger_build)
        self.init_ui(); self._first_build()

    def init_ui(self):
        self.setWindowTitle("Pro Dressing CNC v17.1 – Production"); self.resize(480, 920)
        central = QtWidgets.QWidget(); self.setCentralWidget(central); layout = QtWidgets.QVBoxLayout(central)
        tabs = QtWidgets.QTabWidget(); self.setup_tab_general(tabs); self.setup_tab_sections(tabs); layout.addWidget(tabs)
        self.chk_cnc = QtWidgets.QCheckBox("🔴 ENABLE CNC CUTS"); self.chk_cnc.stateChanged.connect(self.on_param_changed)
        self.chk_hw = QtWidgets.QCheckBox("🔩 SHOW 3D HARDWARE"); self.chk_hw.stateChanged.connect(self.on_param_changed)
        layout.addWidget(self.chk_cnc); layout.addWidget(self.chk_hw)
        self.issue_presenter = IssuePresenter(); layout.addWidget(self.issue_presenter)
        self.btn_build = QtWidgets.QPushButton("🚀 FORCE GENERATE 3D MODEL"); self.btn_build.clicked.connect(self.trigger_build); layout.addWidget(self.btn_build)
        btn_export = QtWidgets.QPushButton("📋 EXPORT CUTLIST (CSV)"); btn_export.clicked.connect(self.export_cutlist); layout.addWidget(btn_export)
        btn_mfg = QtWidgets.QPushButton("🏭 MANUFACTURING REPORT"); btn_mfg.clicked.connect(self.export_manufacturing_report); layout.addWidget(btn_mfg)
        btn_mfg_csv = QtWidgets.QPushButton("🏭 EXPORT MANUFACTURING CSV"); btn_mfg_csv.clicked.connect(self.export_manufacturing_csv); layout.addWidget(btn_mfg_csv)
        btn_executive_csv = QtWidgets.QPushButton("📊 EXPORT EXECUTIVE CSV"); btn_executive_csv.clicked.connect(self.export_executive_csv); layout.addWidget(btn_executive_csv)
        btn_hw = QtWidgets.QPushButton("🔩 HARDWARE REPORT"); btn_hw.clicked.connect(self.export_hardware_report); layout.addWidget(btn_hw)

    def setup_tab_general(self, tabs):
        tab = QtWidgets.QWidget(); form = QtWidgets.QFormLayout(tab)
        self.inp_w = QtWidgets.QDoubleSpinBox(); self.inp_w.setRange(400,5000); self.inp_w.setValue(1800)
        self.inp_h = QtWidgets.QDoubleSpinBox(); self.inp_h.setRange(400,3000); self.inp_h.setValue(2200)
        self.inp_d = QtWidgets.QDoubleSpinBox(); self.inp_d.setRange(200,1000); self.inp_d.setValue(600)
        self.inp_base = QtWidgets.QDoubleSpinBox(); self.inp_base.setRange(0,200); self.inp_base.setValue(80)
        self.inp_back_thickness = QtWidgets.QDoubleSpinBox(); self.inp_back_thickness.setRange(3,18); self.inp_back_thickness.setValue(8)
        self.inp_drawer_depth = QtWidgets.QDoubleSpinBox(); self.inp_drawer_depth.setRange(200,800); self.inp_drawer_depth.setValue(450)
        self.inp_drawer_bottom = QtWidgets.QDoubleSpinBox(); self.inp_drawer_bottom.setRange(3,18); self.inp_drawer_bottom.setValue(8)
        for w in (self.inp_w, self.inp_h, self.inp_d, self.inp_base, self.inp_back_thickness, self.inp_drawer_depth, self.inp_drawer_bottom): w.valueChanged.connect(self.on_param_changed)
        form.addRow("Width:", self.inp_w); form.addRow("Height:", self.inp_h); form.addRow("Depth:", self.inp_d); form.addRow("Base:", self.inp_base)
        form.addRow("Back Thk:", self.inp_back_thickness); form.addRow("Drawer Depth:", self.inp_drawer_depth); form.addRow("Drawer Bottom:", self.inp_drawer_bottom)
        tabs.addTab(tab, "1. Dimensions")

    def setup_tab_sections(self, tabs):
        tab = QtWidgets.QWidget(); layout = QtWidgets.QVBoxLayout(tab)
        top = QtWidgets.QFormLayout(); self.inp_sec = QtWidgets.QSpinBox(); self.inp_sec.setRange(1,10); self.inp_sec.setValue(3)
        top.addRow("Sections:", self.inp_sec); self.inp_sec.valueChanged.connect(self.on_sec_count_changed); layout.addLayout(top)
        layout.addWidget(QtWidgets.QLabel("<b>Section Widths:</b>"))
        self.section_widths_form = QtWidgets.QFormLayout(); layout.addLayout(self.section_widths_form)
        self.lbl_section_width_total = QtWidgets.QLabel(); self.lbl_section_width_status = QtWidgets.QLabel()
        summary = QtWidgets.QFormLayout(); summary.addRow("Total / Cabinet:", self.lbl_section_width_total); summary.addRow("Status:", self.lbl_section_width_status); layout.addLayout(summary)
        self.btn_equalize_sections = QtWidgets.QPushButton("Equalize Sections"); self.btn_equalize_sections.clicked.connect(self.equalize_sections); layout.addWidget(self.btn_equalize_sections)
        layout.addWidget(QtWidgets.QLabel("<b>Customize Section:</b>"))
        sec_form = QtWidgets.QFormLayout()
        self.combo_sec = QtWidgets.QComboBox(); self.combo_sec.currentIndexChanged.connect(self.load_section); sec_form.addRow("Section:", self.combo_sec)
        self.inp_drw = QtWidgets.QSpinBox(); self.inp_drw.setRange(0,10); self.inp_drw_type = QtWidgets.QComboBox(); self.inp_drw_type.addItems(["Inset","Overlay"])
        self.inp_sh = QtWidgets.QSpinBox(); self.inp_sh.setRange(0,15)
        self.inp_door = QtWidgets.QComboBox(); self.inp_door.addItems(["None","Inset","Overlay","Sliding","Glass Inset","Glass Overlay","Glass Sliding"])
        self.inp_door_count = QtWidgets.QSpinBox(); self.inp_door_count.setRange(1,5); self.inp_door_count.setValue(2)
        self.cmb_drawer_layout = QtWidgets.QComboBox(); self.cmb_drawer_layout.addItem("Manual", DrawerLayoutMode.MANUAL); self.cmb_drawer_layout.addItem("Equal", DrawerLayoutMode.EQUAL)

        self.cmb_hinge = QtWidgets.QComboBox()
        self.cmb_hinge.addItem("BLUM CLIP TOP 110", "HINGE_BLUM_110_V1")

        self.cmb_slide = QtWidgets.QComboBox()
        self.cmb_slide.addItem("SOFT CLOSE 450", "DRAWER_SLIDE_SOFTCLOSE_450")

        self.cmb_handle = QtWidgets.QComboBox()
        self.cmb_handle.addItem("HANDLE 128 BLACK", "HANDLE_128_BLACK")
        for w in (self.inp_drw, self.inp_sh, self.inp_door, self.inp_door_count, self.inp_drw_type, self.cmb_drawer_layout,
                  self.cmb_hinge,
                  self.cmb_slide,
                  self.cmb_handle):
            if hasattr(w, 'valueChanged'): w.valueChanged.connect(self.save_current_section)
            elif hasattr(w, 'currentTextChanged'): w.currentTextChanged.connect(self.save_current_section)
            elif hasattr(w, 'currentIndexChanged'): w.currentIndexChanged.connect(self.save_current_section)
        sec_form.addRow("Drawers:", self.inp_drw)
        sec_form.addRow("Drawer Type:", self.inp_drw_type)
        sec_form.addRow("Shelves:", self.inp_sh)
        sec_form.addRow("Door:", self.inp_door)
        sec_form.addRow("Door Count:", self.inp_door_count)
        sec_form.addRow("Layout:", self.cmb_drawer_layout)
        sec_form.addRow("Hinge:", self.cmb_hinge)
        sec_form.addRow("Slide:", self.cmb_slide)
        sec_form.addRow("Handle:", self.cmb_handle)
        layout.addLayout(sec_form); layout.addStretch(); tabs.addTab(tab, "2. Sections")
        self._rebuild_section_width_inputs()

    def on_sec_count_changed(self):
        cnt = self.inp_sec.value()
        for i in range(cnt):
            if i not in self.params.sec_data: self.params.sec_data[i] = SectionConfig()
        self.params.sec_count = cnt; self.is_updating_ui = True; self.combo_sec.clear()
        for i in range(cnt): self.combo_sec.addItem(f"Section {i+1}")
        self.is_updating_ui = False; self.combo_sec.setCurrentIndex(0); self.load_section(); self._rebuild_section_width_inputs(); self.on_param_changed()

    def load_section(self):
        if self.is_updating_ui: return
        idx = self.combo_sec.currentIndex()
        if idx < 0: return
        cfg = self.params.sec_data.get(idx, SectionConfig()); self.is_updating_ui = True
        self.inp_drw.setValue(cfg.drawers); self.inp_drw_type.setCurrentText(cfg.drawer_type); self.inp_sh.setValue(cfg.shelves); self.inp_door.setCurrentText(cfg.doors); self.inp_door_count.setValue(cfg.door_count)
        mode_idx = self.cmb_drawer_layout.findData(cfg.drawer_layout_mode)
        if mode_idx >= 0: self.cmb_drawer_layout.setCurrentIndex(mode_idx)
        self.is_updating_ui = False

    def save_current_section(self):
        if self.is_updating_ui: return
        idx = self.combo_sec.currentIndex()
        if idx < 0: return
        self.params.sec_data[idx] = SectionConfig(drawers=self.inp_drw.value(), drawer_type=self.inp_drw_type.currentText(), shelves=self.inp_sh.value(), doors=self.inp_door.currentText(), door_count=self.inp_door_count.value(), drawer_layout_mode=self.cmb_drawer_layout.currentData())
        self.on_param_changed()

    def _default_section_widths(self):
        count = max(int(getattr(self.params, "sec_count", 0) or 0), 1)
        total_width = float(getattr(self.params, "width", 0.0) or 0.0)
        equal_width = total_width / count if count else 0.0
        return [equal_width for _ in range(count)]

    @staticmethod
    def _widths_are_equal(widths, tolerance=0.01):
        widths = list(widths or [])
        if not widths:
            return True
        first = widths[0]
        return all(abs(width - first) <= tolerance for width in widths)

    def _commit_section_width_inputs(self):
        inputs = list(getattr(self, "section_width_inputs", []) or [])
        if not inputs or getattr(self, "_committing_section_width_inputs", False):
            return
        self._committing_section_width_inputs = True
        try:
            for widget in inputs:
                if hasattr(widget, "interpretText"):
                    widget.interpretText()
        finally:
            self._committing_section_width_inputs = False

    def _section_width_values(self):
        inputs = list(getattr(self, "section_width_inputs", []) or [])
        if inputs:
            self._commit_section_width_inputs()
            return [float(widget.value()) for widget in inputs]
        widths = list(getattr(self.params, "section_widths", []) or [])
        if widths:
            return widths
        return self._default_section_widths()

    def _section_width_issues(self):
        widths = self._section_width_values()
        count = int(getattr(self.params, "sec_count", 0) or 0)
        cabinet_width = float(getattr(self.params, "width", 0.0) or 0.0)
        issues = []
        if len(widths) != count:
            issues.append(
                GeometryIssue(
                    level="ERROR",
                    code="SECTION_WIDTH_COUNT_MISMATCH",
                    message="Section width inputs do not match section count.",
                    domain=Domain.GENERAL,
                )
            )
        for idx, width in enumerate(widths):
            if width <= 0:
                issues.append(
                    GeometryIssue(
                        level="ERROR",
                        code="SECTION_WIDTH_NON_POSITIVE",
                        message=f"Section {idx + 1} width must be greater than zero.",
                        section_index=idx,
                        domain=Domain.GENERAL,
                    )
                )
        if widths and abs(sum(widths) - cabinet_width) > 0.01:
            issues.append(
                GeometryIssue(
                    level="ERROR",
                    code="SECTION_WIDTH_TOTAL_MISMATCH",
                    message="Section widths must total the cabinet width.",
                    component="Section Width Editor",
                    domain=Domain.GENERAL,
                )
            )
        return issues

    def _section_widths_valid(self):
        return not self._section_width_issues()

    def _section_width_validation_message(self):
        widths = self._section_width_values()
        total = sum(widths)
        cabinet_width = float(getattr(self.params, "width", 0.0) or 0.0)
        issues = self._section_width_issues()
        if not issues:
            return f"OK ({total:.1f} / {cabinet_width:.1f})"
        return f"ERROR: {total:.1f} / {cabinet_width:.1f}"

    def _update_section_width_status(self):
        widths = self._section_width_values()
        issues = self._section_width_issues()
        if hasattr(self, "lbl_section_width_total"):
            self.lbl_section_width_total.setText(f"{sum(widths):.1f} / {float(getattr(self.params, 'width', 0.0) or 0.0):.1f}")
        if hasattr(self, "lbl_section_width_status"):
            self.lbl_section_width_status.setText(self._section_width_validation_message())
        if hasattr(self, "btn_build"):
            self.btn_build.setEnabled(not issues)
        return issues

    def _sync_section_width_inputs(self, widths):
        if not getattr(self, "section_width_inputs", None):
            return
        self.is_updating_ui = True
        try:
            for widget, width in zip(self.section_width_inputs, widths):
                if hasattr(widget, "setValue"):
                    widget.setValue(width)
        finally:
            self.is_updating_ui = False

    def _apply_section_widths(self, widths):
        widths = list(widths or [])
        self.params.section_widths = widths
        self._sync_section_width_inputs(widths)
        self._last_cabinet_width = float(getattr(self.params, "width", 0.0) or 0.0)
        self._update_section_width_status()

    def _rebalance_section_widths_for_count_change(self):
        self._apply_section_widths(self._default_section_widths())

    def _rebalance_section_widths_for_width_change(self, previous_width, new_width):
        widths = list(self._section_width_values())
        expected_count = max(int(getattr(self.params, "sec_count", 0) or 0), 0)
        if not widths or len(widths) != expected_count:
            self._apply_section_widths(self._default_section_widths())
            return
        if self._widths_are_equal(widths):
            self._apply_section_widths([new_width / len(widths) for _ in widths])
            return
        total = sum(widths)
        if total <= 0:
            self._apply_section_widths(self._default_section_widths())
            return
        scale = new_width / total
        self._apply_section_widths([width * scale for width in widths])

    def _clear_layout(self, layout):
        if layout is None or not hasattr(layout, "count"):
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget() if hasattr(item, "widget") else None
            child_layout = item.layout() if hasattr(item, "layout") else None
            if widget is not None and hasattr(widget, "setParent"):
                widget.setParent(None)
            if child_layout is not None:
                self._clear_layout(child_layout)

    def _rebuild_section_width_inputs(self):
        if not hasattr(self, "section_widths_form"):
            return
        self.is_updating_ui = True
        try:
            self._clear_layout(self.section_widths_form)
            self.section_width_inputs = []
            widths = self._default_section_widths()
            for index, width in enumerate(widths):
                spin = QtWidgets.QDoubleSpinBox()
                if hasattr(spin, "setRange"):
                    spin.setRange(1, 5000)
                if hasattr(spin, "setDecimals"):
                    spin.setDecimals(2)
                if hasattr(spin, "setValue"):
                    spin.setValue(width)
                if hasattr(spin, "valueChanged"):
                    spin.valueChanged.connect(self.on_section_width_changed)
                if hasattr(spin, "editingFinished"):
                    spin.editingFinished.connect(self.on_section_width_changed)
                self.section_width_inputs.append(spin)
                self.section_widths_form.addRow(f"Section {index + 1}:", spin)
            self._apply_section_widths(widths)
        finally:
            self.is_updating_ui = False

    def on_section_width_changed(self, *args):
        if self.is_updating_ui or getattr(self, "_committing_section_width_inputs", False):
            return
        self._commit_section_width_inputs()
        widths = self._section_width_values()
        self._apply_section_widths(widths)
        self.on_param_changed()

    def equalize_sections(self):
        if getattr(self, "is_updating_ui", False):
            return
        self._apply_section_widths(self._default_section_widths())
        self.on_param_changed()

    def on_param_changed(self):
        if self.is_updating_ui: return
        previous_width = float(getattr(self, "_last_cabinet_width", getattr(self.params, "width", 0.0)) or 0.0)
        self.params.width = self.inp_w.value(); self.params.height = self.inp_h.value(); self.params.depth = self.inp_d.value(); self.params.base_height = self.inp_base.value(); self.params.back_thickness = self.inp_back_thickness.value(); self.params.drawer_depth = self.inp_drawer_depth.value(); self.params.drawer_bottom_thickness = self.inp_drawer_bottom.value()
        self.params.cnc_mode = self.chk_cnc.isChecked(); self.params.hw_mode = self.chk_hw.isChecked(); self.params.sec_count = self.inp_sec.value()
        new_width = float(self.params.width or 0.0)
        if not getattr(self, "section_width_inputs", None):
            self.params.section_widths = self._default_section_widths()
        elif abs(new_width - previous_width) > 0.01:
            self._rebalance_section_widths_for_width_change(previous_width, new_width)
        else:
            self._update_section_width_status()
        self._last_cabinet_width = new_width

        self.params.hinge_sku = self.cmb_hinge.currentData()
        self.params.slide_sku = self.cmb_slide.currentData()
        self.params.handle_sku = self.cmb_handle.currentData()
        if not self._section_widths_valid():
            if hasattr(self, "build_timer"):
                self.build_timer.stop()
            return
        if hasattr(self, "build_timer"):
            self.build_timer.start(300)

    def _first_build(self): self.on_param_changed()

    def trigger_build(self):
        try:
            self._commit_section_width_inputs()
            width_issues = self._section_width_issues()
            if width_issues:
                self.val_state = ValidationState(); self.val_state.issues = width_issues
                self.issue_presenter.display_issues(self.val_state.issues)
                if hasattr(self, "build_timer"):
                    self.build_timer.stop()
                return

            self.params.section_widths = self._section_width_values()
            cabinet = Cabinet(self.params)
            validation_service = ValidationService(cabinet, self.builder.mat); self.val_state = validation_service.validate_only(); self.issue_presenter.display_issues(self.val_state.issues)
            
            if self.val_state.has_errors:
                for issue in self.val_state.issues:
                    logger.error(f"[ISSUE] {issue}")
                logger.error("Blocked by constraint errors.")
                return

            specification = BaseCabinetSpecificationAdapter.from_cabinet_params(self.params)
            attach_base_cabinet_engineering_models(cabinet, specification)
            self.builder.build(cabinet)
            logger.info("Build completed.")
        except Exception as e: logger.error(f"Failure: {e}")

    def export_cutlist(self):
        print("[EXPORT CUTLIST STARTED]")
        if not self.builder.scene_graph:
            logger.warning("No scene graph to export.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save BOM", "BOM.csv", "CSV (*.csv)")
        if not path: return
        from exports.bom_engine import BOMEngine
        report = BOMEngine.generate(self.builder.scene_graph)

        cost = CostEngine.generate(report, self.builder.scene_graph)

        BOMEngine.export_csv(report, path)

        logger.info(
            f"Cost Report | "
            f"Material={cost.material_cost:.0f} DH | "
            f"Total={cost.total_cost:.0f} DH | "
            f"Sell={cost.selling_price:.0f} DH"
        )
        QtWidgets.QMessageBox.information(self, "BOM Exported", f"BOM saved to {path}")

    def export_manufacturing_report(self):

        from exports.manufacturing_report import ManufacturingReportEngine

        report = ManufacturingReportEngine.generate(
            self.builder.scene_graph
        )

        print()
        print("========== MANUFACTURING REPORT ==========")

        for line in report.lines:
            print(line.part_id)
            print("   ", line.description)

        print("==========================================")

    def export_manufacturing_csv(self):

        if not self.builder.scene_graph:
            return

        from exports.manufacturing_report import ManufacturingReportEngine

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Manufacturing Report",
            "Manufacturing.csv",
            "CSV (*.csv)"
        )

        if not path:
            return

        report = ManufacturingReportEngine.generate(
            self.builder.scene_graph
        )

        ManufacturingReportEngine.export_csv(
            report,
            path
        )

        QtWidgets.QMessageBox.information(
            self,
            "Manufacturing Exported",
            f"Manufacturing report saved to\n{path}"
        )

    def export_executive_csv(self):

        if not self.builder.scene_graph:
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save Executive Report",
            "Executive_Report.csv",
            "CSV (*.csv)"
        )

        if not path:
            return

        from exports.manufacturing_executive_export import (
            ManufacturingExecutiveExport
        )

        report = ManufacturingExecutiveExport.generate(
            self.builder.scene_graph
        )

        ManufacturingExecutiveExport.export_csv(
            report,
            path
        )

        QtWidgets.QMessageBox.information(
            self,
            "Executive Report Exported",
            f"Executive report saved to\n{path}"
        )


    def export_hardware_report(self):

        from exports.hardware_report import (
            HardwareReportEngine
        )

        report = HardwareReportEngine.generate(
            self.builder.scene_graph
        )

        print()
        print("===== HARDWARE REPORT =====")

        print(
            "MINIFIX =",
            report.minifix_count
        )

        print(
            "DOWEL =",
            report.dowel_count
        )

        print(
            "HARDWARE COST =",
            report.hardware_cost,
            "DH"
        )

        print("==========================")
