from core.qt_compat import QtWidgets, QtCore
from shared.contracts import CabinetParams, SectionConfig; from shared.enums import DrawerLayoutMode
from shared.issues import ValidationState; from core.logging_config import logger
from engine.cabinet import Cabinet; from engine.cabinet_builder import CabinetBuilder
from services.validation_service import ValidationService; from ui.issue_presenter import IssuePresenter
import csv
from costing.cost_engine import CostEngine

class UIManager(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__(); self.params = CabinetParams(); self.builder = CabinetBuilder(); self.val_state = ValidationState()
        self.is_updating_ui = False; self.build_timer = QtCore.QTimer(); self.build_timer.setSingleShot(True); self.build_timer.timeout.connect(self.trigger_build)
        self.init_ui(); self._first_build()

    def init_ui(self):
        self.setWindowTitle("Pro Dressing CNC v17.1 – Production"); self.resize(480, 920)
        central = QtWidgets.QWidget(); self.setCentralWidget(central); layout = QtWidgets.QVBoxLayout(central)
        tabs = QtWidgets.QTabWidget(); self.setup_tab_general(tabs); self.setup_tab_sections(tabs); layout.addWidget(tabs)
        self.chk_cnc = QtWidgets.QCheckBox("🔴 ENABLE CNC CUTS"); self.chk_cnc.stateChanged.connect(self.on_param_changed)
        self.chk_hw = QtWidgets.QCheckBox("🔩 SHOW 3D HARDWARE"); self.chk_hw.stateChanged.connect(self.on_param_changed)
        layout.addWidget(self.chk_cnc); layout.addWidget(self.chk_hw)
        self.issue_presenter = IssuePresenter(); layout.addWidget(self.issue_presenter)
        btn_build = QtWidgets.QPushButton("🚀 FORCE GENERATE 3D MODEL"); btn_build.clicked.connect(self.trigger_build); layout.addWidget(btn_build)
        btn_export = QtWidgets.QPushButton("📋 EXPORT CUTLIST (CSV)"); btn_export.clicked.connect(self.export_cutlist); layout.addWidget(btn_export)

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

    def on_sec_count_changed(self):
        cnt = self.inp_sec.value()
        for i in range(cnt):
            if i not in self.params.sec_data: self.params.sec_data[i] = SectionConfig()
        self.params.sec_count = cnt; self.is_updating_ui = True; self.combo_sec.clear()
        for i in range(cnt): self.combo_sec.addItem(f"Section {i+1}")
        self.is_updating_ui = False; self.combo_sec.setCurrentIndex(0); self.load_section(); self.on_param_changed()

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

    def on_param_changed(self):
        if self.is_updating_ui: return
        self.params.width = self.inp_w.value(); self.params.height = self.inp_h.value(); self.params.depth = self.inp_d.value(); self.params.base_height = self.inp_base.value(); self.params.back_thickness = self.inp_back_thickness.value(); self.params.drawer_depth = self.inp_drawer_depth.value(); self.params.drawer_bottom_thickness = self.inp_drawer_bottom.value()
        self.params.cnc_mode = self.chk_cnc.isChecked(); self.params.hw_mode = self.chk_hw.isChecked(); self.params.sec_count = self.inp_sec.value()

        self.params.hinge_sku = self.cmb_hinge.currentData()
        self.params.slide_sku = self.cmb_slide.currentData()
        self.params.handle_sku = self.cmb_handle.currentData()
        self.build_timer.start(300)

    def _first_build(self): self.on_param_changed()

    def trigger_build(self):
        try:
            cabinet = Cabinet(self.params)
            validation_service = ValidationService(cabinet, self.builder.mat); self.val_state = validation_service.validate_only(); self.issue_presenter.display_issues(self.val_state.issues)
            
            if self.val_state.has_errors:
                for issue in self.val_state.issues:
                    logger.error(f"[ISSUE] {issue}")
                logger.error("Blocked by constraint errors.")
                return

            self.builder.build(cabinet); logger.info("Build completed.")
        except Exception as e: logger.error(f"Failure: {e}")

    def export_cutlist(self):
        if not self.builder.scene_graph:
            logger.warning("No scene graph to export.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save BOM", "BOM.csv", "CSV (*.csv)")
        if not path: return
        from exports.bom_engine import BOMEngine
        report = BOMEngine.generate(self.builder.scene_graph)

        cost = CostEngine.generate(report)

        BOMEngine.export_csv(report, path)

        logger.info(
            f"Cost Report | "
            f"Material={cost.material_cost:.0f} DH | "
            f"Total={cost.total_cost:.0f} DH | "
            f"Sell={cost.selling_price:.0f} DH"
        )
        QtWidgets.QMessageBox.information(self, "BOM Exported", f"BOM saved to {path}")
