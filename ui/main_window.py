"""
Main Window for FourierSplineStudio.
Integrates Canvas, Control Panel, Formula View, and Harmonics View.
"""

import time
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QSplitter,
    QTabWidget, QStatusBar, QLabel
)
from PyQt5.QtCore import Qt, QTimer

try:
    from ui.canvas import SplineCanvas
    from ui.control_panel import ControlPanel
    from ui.formula_view import FormulaView
    from ui.harmonics_view import HarmonicsView
    from core.splines import SPLINE_ALGORITHMS
    from core.fourier import FourierSeries2D
    from core.presets import PRESETS
except (ImportError, ValueError):
    from .canvas import SplineCanvas
    from .control_panel import ControlPanel
    from .formula_view import FormulaView
    from .harmonics_view import HarmonicsView
    from ..core.splines import SPLINE_ALGORITHMS
    from ..core.fourier import FourierSeries2D
    from ..core.presets import PRESETS


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Fourier & Spline Studio — XY Epicycles & Funktionsgenerator")
        self.resize(1300, 850)

        # State
        self.current_spline_name = "Catmull-Rom (Interpolierend)"
        self.is_closed = True
        self.is_playing = False
        self.animation_speed = 1.0  # revolutions per 10 seconds
        self.last_anim_time = time.time()
        self.num_epicycles = 25

        self.init_ui()
        self.setup_animation_timer()

        # Load default preset shape
        self.load_preset("Herz (Heart)")

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(0)

        # Splitter between Canvas Tabs and Control Panel
        splitter = QSplitter(Qt.Horizontal)

        # Left / Center: Tab Widget
        self.tabs = QTabWidget()
        self.canvas = SplineCanvas()
        self.formula_view = FormulaView()
        self.harmonics_view = HarmonicsView()

        self.tabs.addTab(self.canvas, "🎨 1. XY-Zeichenebene & Epizyklen")
        self.tabs.addTab(self.formula_view, "📐 2. Funktionsausgabe & Export")
        self.tabs.addTab(self.harmonics_view, "📊 3. Epizyklen-Tabelle (Harmonische)")

        # Right: Control Panel
        self.control_panel = ControlPanel()
        self.control_panel.setMinimumWidth(330)
        self.control_panel.setMaximumWidth(400)

        splitter.addWidget(self.tabs)
        splitter.addWidget(self.control_panel)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.lbl_status_coords = QLabel("X: 0.0, Y: 0.0")
        self.lbl_status_pts = QLabel("Punkte: 0")
        self.lbl_status_help = QLabel("Mausrad: Zoom | Linksklick: Punkt hinzufügen/ziehen | Rechtsklick: Punkt löschen | Leertaste+Ziehen: Verschieben")
        self.lbl_status_help.setStyleSheet("color: #94a3b8;")

        self.status_bar.addWidget(self.lbl_status_coords, 1)
        self.status_bar.addWidget(self.lbl_status_pts, 1)
        self.status_bar.addPermanentWidget(self.lbl_status_help)

        self._connect_signals()

    def _connect_signals(self):
        # Canvas Signals
        self.canvas.points_changed.connect(self._recalculate_spline_and_fourier)
        self.canvas.cursor_moved.connect(self._on_cursor_moved)

        # Control Panel - Spline
        self.control_panel.spline_type_changed.connect(self._on_spline_type_changed)
        self.control_panel.closed_changed.connect(self._on_closed_changed)
        self.control_panel.preset_selected.connect(self.load_preset)
        self.control_panel.freehand_toggled.connect(self._on_freehand_toggled)
        self.control_panel.clear_points_clicked.connect(self._clear_points)
        self.control_panel.reverse_points_clicked.connect(self._reverse_points)
        self.control_panel.reset_view_clicked.connect(self.canvas.reset_view)

        # Control Panel - Fourier & Animation
        self.control_panel.epicycles_count_changed.connect(self._on_epicycles_count_changed)
        self.control_panel.play_toggled.connect(self._on_play_toggled)
        self.control_panel.speed_changed.connect(self._on_speed_changed)
        self.control_panel.scrub_t_changed.connect(self._on_scrub_t_changed)

        # Control Panel - Display Toggles
        self.control_panel.toggle_circles.connect(lambda v: self._set_layer_vis("circles", v))
        self.control_panel.toggle_vectors.connect(lambda v: self._set_layer_vis("vectors", v))
        self.control_panel.toggle_recon.connect(lambda v: self._set_layer_vis("recon", v))
        self.control_panel.toggle_original.connect(lambda v: self._set_layer_vis("original", v))
        self.control_panel.toggle_points.connect(lambda v: self._set_layer_vis("points", v))
        self.control_panel.toggle_trail.connect(lambda v: self._set_layer_vis("trail", v))
        self.control_panel.toggle_grid.connect(lambda v: self._set_layer_vis("grid", v))

    def setup_animation_timer(self):
        self.anim_timer = QTimer(self)
        self.anim_timer.setInterval(16)  # ~60 fps
        self.anim_timer.timeout.connect(self._on_animation_frame)
        self.last_anim_time = time.time()

    def _on_animation_frame(self):
        now = time.time()
        dt = now - self.last_anim_time
        self.last_anim_time = now

        # One full loop in 8 seconds at 1.0x speed
        cycle_duration = 8.0 / max(0.01, self.animation_speed)
        delta_t = dt / cycle_duration
        new_t = (self.canvas.current_t + delta_t) % 1.0

        self.canvas.set_time(new_t)
        self.control_panel.update_t_display(new_t)

    def _on_play_toggled(self, playing: bool):
        self.is_playing = playing
        if playing:
            self.last_anim_time = time.time()
            self.anim_timer.start()
        else:
            self.anim_timer.stop()

    def _on_speed_changed(self, speed: float):
        self.animation_speed = speed

    def _on_scrub_t_changed(self, t: float):
        self.canvas.set_time(t)

    def _on_cursor_moved(self, x: float, y: float):
        self.lbl_status_coords.setText(f"X: {x:.1f}, Y: {y:.1f}")

    def _on_spline_type_changed(self, name: str):
        self.current_spline_name = name
        self._recalculate_spline_and_fourier()

    def _on_closed_changed(self, closed: bool):
        self.is_closed = closed
        self.canvas.is_closed = closed
        self._recalculate_spline_and_fourier()

    def _on_freehand_toggled(self, enabled: bool):
        self.canvas.freehand_mode = enabled
        if enabled:
            self.status_bar.showMessage("Freihand-Modus aktiv: Maus auf der Zeichenebene gedrückt halten und zeichnen!", 4000)

    def _clear_points(self):
        self.canvas.set_control_points([])

    def _reverse_points(self):
        pts = list(reversed(self.canvas.control_points))
        self.canvas.set_control_points(pts)

    def _set_layer_vis(self, layer: str, visible: bool):
        if layer == "circles":
            self.canvas.show_epicycle_circles = visible
        elif layer == "vectors":
            self.canvas.show_epicycle_vectors = visible
        elif layer == "recon":
            self.canvas.show_reconstructed_curve = visible
        elif layer == "original":
            self.canvas.show_original_spline = visible
        elif layer == "points":
            self.canvas.show_control_points = visible
            self.canvas.show_control_polygon = visible
        elif layer == "trail":
            self.canvas.show_trail = visible
        elif layer == "grid":
            self.canvas.show_grid = visible
            self.canvas.show_axes = visible
        self.canvas.update()

    def _on_epicycles_count_changed(self, count: int):
        self.num_epicycles = count
        self.canvas.set_num_epicycles(count)
        self._update_formula_and_metrics()

    def load_preset(self, preset_name: str):
        if preset_name in PRESETS:
            points_fn = PRESETS[preset_name]
            pts = points_fn()
            # If wave preset, default to open curve
            if "Welle" in preset_name:
                self.control_panel.chk_closed.setChecked(False)
            else:
                self.control_panel.chk_closed.setChecked(True)

            self.canvas.set_control_points(pts)
            self.canvas.reset_view()

    def _recalculate_spline_and_fourier(self):
        pts = self.canvas.control_points
        self.lbl_status_pts.setText(f"Punkte: {len(pts)}")

        if len(pts) < 2:
            self.canvas.set_spline_curve(np.zeros((0, 2)))
            self.canvas.set_fourier_series(None)
            self.formula_view.set_epicycles([])
            self.harmonics_view.set_epicycles([])
            self.control_panel.update_metrics(0.0, 0.0, 0.0)
            return

        # 1. Compute Spline
        spline_fn = SPLINE_ALGORITHMS.get(self.current_spline_name, SPLINE_ALGORITHMS["Catmull-Rom (Interpolierend)"])
        curve_points = spline_fn(pts, num_samples=600, closed=self.is_closed)
        self.canvas.set_spline_curve(curve_points)

        # 2. Compute Fourier Series
        fourier = FourierSeries2D(curve_points)
        self.canvas.set_fourier_series(fourier)
        self.canvas.set_num_epicycles(self.num_epicycles)

        # 3. Update Table and Formulas
        self.harmonics_view.set_epicycles(fourier.sorted_epicycles)
        self._update_formula_and_metrics()

    def _update_formula_and_metrics(self):
        if self.canvas.fourier_series is not None:
            active_eps = self.canvas.fourier_series.get_active_epicycles(self.num_epicycles)
            self.formula_view.set_epicycles(active_eps)

            mean_err, max_err = self.canvas.fourier_series.compute_approximation_error(self.num_epicycles)
            total_energy = sum(ep.radius ** 2 for ep in self.canvas.fourier_series.sorted_epicycles)
            active_energy = sum(ep.radius ** 2 for ep in active_eps)
            energy_pct = (active_energy / total_energy * 100.0) if total_energy > 0 else 0.0

            self.control_panel.update_metrics(mean_err, max_err, energy_pct)
