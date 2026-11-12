"""
Control Panel for Splines, Fourier Epicycles, and Animation.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QComboBox, QCheckBox, QSlider, QSpinBox, QPushButton,
    QDoubleSpinBox, QScrollArea, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal

try:
    from core.splines import SPLINE_ALGORITHMS
    from core.presets import PRESETS
except (ImportError, ValueError):
    from ..core.splines import SPLINE_ALGORITHMS
    from ..core.presets import PRESETS


class ControlPanel(QWidget):
    # Signals
    spline_type_changed = pyqtSignal(str)
    closed_changed = pyqtSignal(bool)
    preset_selected = pyqtSignal(str)
    freehand_toggled = pyqtSignal(bool)
    clear_points_clicked = pyqtSignal()
    reverse_points_clicked = pyqtSignal()
    reset_view_clicked = pyqtSignal()

    epicycles_count_changed = pyqtSignal(int)
    play_toggled = pyqtSignal(bool)
    speed_changed = pyqtSignal(float)
    scrub_t_changed = pyqtSignal(float)

    toggle_circles = pyqtSignal(bool)
    toggle_vectors = pyqtSignal(bool)
    toggle_recon = pyqtSignal(bool)
    toggle_original = pyqtSignal(bool)
    toggle_points = pyqtSignal(bool)
    toggle_trail = pyqtSignal(bool)
    toggle_grid = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        # Scroll area in case screen height is small
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # -------------------------------------------------------------
        # 1. Spline Configuration
        # -------------------------------------------------------------
        spline_group = QGroupBox("1. Spline Kurven-Konfiguration")
        sg_layout = QVBoxLayout(spline_group)
        sg_layout.setSpacing(8)

        # Spline Type
        lbl_type = QLabel("Spline-Algorithmus:")
        self.combo_spline = QComboBox()
        for name in SPLINE_ALGORITHMS.keys():
            self.combo_spline.addItem(name)
        self.combo_spline.currentTextChanged.connect(self.spline_type_changed.emit)
        sg_layout.addWidget(lbl_type)
        sg_layout.addWidget(self.combo_spline)

        # Presets
        lbl_preset = QLabel("Form-Vorlagen (Presets):")
        self.combo_preset = QComboBox()
        self.combo_preset.addItem("-- Vorlage auswählen --")
        for name in PRESETS.keys():
            self.combo_preset.addItem(name)
        self.combo_preset.currentIndexChanged.connect(self._on_preset_changed)
        sg_layout.addWidget(lbl_preset)
        sg_layout.addWidget(self.combo_preset)

        # Closed Loop Checkbox
        self.chk_closed = QCheckBox("Geschlossene Kurve (Closed Loop)")
        self.chk_closed.setChecked(True)
        self.chk_closed.toggled.connect(self.closed_changed.emit)
        sg_layout.addWidget(self.chk_closed)

        # Action Buttons
        btn_layout = QHBoxLayout()
        self.btn_freehand = QPushButton("✏️ Freihand Zeichnen")
        self.btn_freehand.setCheckable(True)
        self.btn_freehand.toggled.connect(self.freehand_toggled.emit)
        self.btn_freehand.setObjectName("recordButton")

        self.btn_reset_view = QPushButton("🔍 Ansicht anpassen")
        self.btn_reset_view.clicked.connect(self.reset_view_clicked.emit)

        btn_layout.addWidget(self.btn_freehand)
        btn_layout.addWidget(self.btn_reset_view)
        sg_layout.addLayout(btn_layout)

        btn_layout2 = QHBoxLayout()
        self.btn_reverse = QPushButton("🔄 Richtung umkehren")
        self.btn_reverse.clicked.connect(self.reverse_points_clicked.emit)

        self.btn_clear = QPushButton("🗑️ Alle Punkte löschen")
        self.btn_clear.clicked.connect(self.clear_points_clicked.emit)

        btn_layout2.addWidget(self.btn_reverse)
        btn_layout2.addWidget(self.btn_clear)
        sg_layout.addLayout(btn_layout2)

        layout.addWidget(spline_group)

        # -------------------------------------------------------------
        # 2. Fourier Epicycles Settings
        # -------------------------------------------------------------
        fourier_group = QGroupBox("2. Fourier Epizyklen (Harmonische)")
        fg_layout = QVBoxLayout(fourier_group)
        fg_layout.setSpacing(8)

        # Number of Epicycles Slider + SpinBox
        lbl_epi = QLabel("Anzahl Epizyklen (Harmonische N):")
        fg_layout.addWidget(lbl_epi)

        epi_row = QHBoxLayout()
        self.slider_epicycles = QSlider(Qt.Horizontal)
        self.slider_epicycles.setRange(1, 120)
        self.slider_epicycles.setValue(15)

        self.spin_epicycles = QSpinBox()
        self.spin_epicycles.setRange(1, 200)
        self.spin_epicycles.setValue(15)
        self.spin_epicycles.setFixedWidth(65)

        self.slider_epicycles.valueChanged.connect(self.spin_epicycles.setValue)
        self.spin_epicycles.valueChanged.connect(self.slider_epicycles.setValue)
        self.spin_epicycles.valueChanged.connect(self.epicycles_count_changed.emit)

        epi_row.addWidget(self.slider_epicycles)
        epi_row.addWidget(self.spin_epicycles)
        fg_layout.addLayout(epi_row)

        # Approximation Error HUD
        err_box = QFrame()
        err_box.setStyleSheet("background-color: #0f172a; border-radius: 6px; padding: 6px;")
        err_layout = QVBoxLayout(err_box)
        err_layout.setContentsMargins(6, 6, 6, 6)
        err_layout.setSpacing(3)

        self.lbl_error_avg = QLabel("Mittlerer Fehler: 0.00 px")
        self.lbl_error_avg.setObjectName("metricLabel")
        self.lbl_error_max = QLabel("Maximaler Fehler: 0.00 px")
        self.lbl_error_max.setObjectName("metricLabel")
        self.lbl_energy = QLabel("Approximierte Energie: 100.0%")
        self.lbl_energy.setObjectName("metricLabel")

        err_layout.addWidget(self.lbl_error_avg)
        err_layout.addWidget(self.lbl_error_max)
        err_layout.addWidget(self.lbl_energy)
        fg_layout.addWidget(err_box)

        layout.addWidget(fourier_group)

        # -------------------------------------------------------------
        # 3. Animation Controls
        # -------------------------------------------------------------
        anim_group = QGroupBox("3. Epizyklen Animation & Zeit")
        ag_layout = QVBoxLayout(anim_group)
        ag_layout.setSpacing(8)

        # Play / Pause
        self.btn_play = QPushButton("▶ Animation Starten")
        self.btn_play.setObjectName("playButton")
        self.btn_play.setCheckable(True)
        self.btn_play.toggled.connect(self._on_play_toggled)
        ag_layout.addWidget(self.btn_play)

        # Speed Control
        spd_row = QHBoxLayout()
        lbl_speed = QLabel("Geschwindigkeit:")
        self.slider_speed = QSlider(Qt.Horizontal)
        self.slider_speed.setRange(10, 400)
        self.slider_speed.setValue(100)  # 1.0x

        self.lbl_speed_val = QLabel("1.0x")
        self.lbl_speed_val.setFixedWidth(45)

        self.slider_speed.valueChanged.connect(self._on_speed_changed)
        spd_row.addWidget(lbl_speed)
        spd_row.addWidget(self.slider_speed)
        spd_row.addWidget(self.lbl_speed_val)
        ag_layout.addLayout(spd_row)

        # Time parameter t scrub slider
        self.lbl_t_val = QLabel("Parameter t: 0.000 (0°)")
        ag_layout.addWidget(self.lbl_t_val)

        self.slider_t = QSlider(Qt.Horizontal)
        self.slider_t.setRange(0, 1000)
        self.slider_t.setValue(0)
        self.slider_t.valueChanged.connect(self._on_slider_t_changed)
        ag_layout.addWidget(self.slider_t)

        layout.addWidget(anim_group)

        # -------------------------------------------------------------
        # 4. Display & Layer Visibility Toggles
        # -------------------------------------------------------------
        view_group = QGroupBox("4. Ansichts-Ebenen ein/ausblenden")
        vg_layout = QVBoxLayout(view_group)
        vg_layout.setSpacing(6)

        self.chk_circles = QCheckBox("Epizyklen-Kreise (Circles)")
        self.chk_circles.setChecked(True)
        self.chk_circles.toggled.connect(self.toggle_circles.emit)

        self.chk_vectors = QCheckBox("Vektorpfeile (Radii)")
        self.chk_vectors.setChecked(True)
        self.chk_vectors.toggled.connect(self.toggle_vectors.emit)

        self.chk_recon = QCheckBox("Fourier-Rekonstruktion (Pfad)")
        self.chk_recon.setChecked(True)
        self.chk_recon.toggled.connect(self.toggle_recon.emit)

        self.chk_original = QCheckBox("Original-Spline (Blau)")
        self.chk_original.setChecked(True)
        self.chk_original.toggled.connect(self.toggle_original.emit)

        self.chk_points = QCheckBox("Kontrollpunkte & Netz")
        self.chk_points.setChecked(True)
        self.chk_points.toggled.connect(self.toggle_points.emit)

        self.chk_trail = QCheckBox("Zeichenspur (Pen Trail)")
        self.chk_trail.setChecked(True)
        self.chk_trail.toggled.connect(self.toggle_trail.emit)

        self.chk_grid = QCheckBox("Koordinatengitter & Achsen")
        self.chk_grid.setChecked(True)
        self.chk_grid.toggled.connect(self.toggle_grid.emit)

        for chk in [self.chk_circles, self.chk_vectors, self.chk_recon,
                    self.chk_original, self.chk_points, self.chk_trail, self.chk_grid]:
            vg_layout.addWidget(chk)

        layout.addWidget(view_group)
        layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def _on_preset_changed(self, index: int):
        if index > 0:
            name = self.combo_preset.currentText()
            self.preset_selected.emit(name)
            # Reset dropdown back to prompt
            self.combo_preset.blockSignals(True)
            self.combo_preset.setCurrentIndex(0)
            self.combo_preset.blockSignals(False)

    def _on_play_toggled(self, checked: bool):
        if checked:
            self.btn_play.setText("⏸ Animation Pausieren")
            self.btn_play.setStyleSheet("background-color: #d97706; border-color: #f59e0b;")
        else:
            self.btn_play.setText("▶ Animation Starten")
            self.btn_play.setStyleSheet("")
        self.play_toggled.emit(checked)

    def _on_speed_changed(self, value: int):
        speed = value / 100.0
        self.lbl_speed_val.setText(f"{speed:.1f}x")
        self.speed_changed.emit(speed)

    def _on_slider_t_changed(self, value: int):
        t = value / 1000.0
        deg = int(t * 360)
        self.lbl_t_val.setText(f"Parameter t: {t:.3f} ({deg}°)")
        self.scrub_t_changed.emit(t)

    def update_t_display(self, t: float):
        self.slider_t.blockSignals(True)
        val = int((t % 1.0) * 1000)
        self.slider_t.setValue(val)
        deg = int(t * 360)
        self.lbl_t_val.setText(f"Parameter t: {t:.3f} ({deg}°)")
        self.slider_t.blockSignals(False)

    def update_metrics(self, avg_err: float, max_err: float, energy: float):
        self.lbl_error_avg.setText(f"Mittlerer Fehler: {avg_err:.2f} px")
        self.lbl_error_max.setText(f"Maximaler Fehler: {max_err:.2f} px")
        self.lbl_energy.setText(f"Harmonische Energie: {energy:.2f}%")
