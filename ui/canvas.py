"""
Interactive XY Plane Canvas with QPainter.
Handles grid, pan & zoom, control point manipulation, spline rendering,
and real-time 3Blue1Brown-style Fourier Epicycles animation.
"""

import math
from typing import List, Tuple, Optional
import numpy as np

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, QPointF, QRectF, pyqtSignal
from PyQt5.QtGui import (
    QPainter, QPen, QColor, QBrush, QFont, QPainterPath,
    QCursor, QPolygonF
)

try:
    from core.fourier import FourierSeries2D, Epicycle
except (ImportError, ValueError):
    from ..core.fourier import FourierSeries2D, Epicycle


class SplineCanvas(QWidget):
    # Signals
    points_changed = pyqtSignal()
    cursor_moved = pyqtSignal(float, float)
    time_changed = pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

        # Coordinate System & Viewport
        self.zoom = 1.0
        self.pan_offset = QPointF(0, 0)
        self.is_first_resize = True

        # Control Points (World coordinates)
        self.control_points: List[Tuple[float, float]] = []
        self.selected_point_idx: Optional[int] = None
        self.hovered_point_idx: Optional[int] = None

        # Spline data
        self.spline_curve_points: np.ndarray = np.zeros((0, 2))
        self.is_closed = True

        # Fourier Data
        self.fourier_series: Optional[FourierSeries2D] = None
        self.reconstructed_curve: np.ndarray = np.zeros((0, 2))
        self.num_epicycles_to_draw = 15

        # Animation & Time
        self.current_t = 0.0  # normalized [0.0, 1.0]

        # Interaction Modes
        self.freehand_mode = False
        self.is_freehand_drawing = False
        self.freehand_raw_points: List[Tuple[float, float]] = []

        self.is_panning = False
        self.pan_start = QPointF()
        self.is_space_pressed = False

        # Visibility Toggles
        self.show_grid = True
        self.show_axes = True
        self.show_control_polygon = True
        self.show_control_points = True
        self.show_original_spline = True
        self.show_reconstructed_curve = True
        self.show_epicycle_circles = True
        self.show_epicycle_vectors = True
        self.show_trail = True
        self.show_pen_tip = True

        # Precomputed trail buffer
        self.trail_points: List[Tuple[float, float]] = []

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.is_first_resize:
            # Center the coordinate system origin at the canvas center
            self.pan_offset = QPointF(self.width() / 2.0, self.height() / 2.0)
            self.is_first_resize = False

    # -------------------------------------------------------------
    # Coordinate Transforms
    # -------------------------------------------------------------
    def world_to_screen(self, x: float, y: float) -> QPointF:
        """Convert world coordinates (where +Y is UP) to screen pixels."""
        u = self.pan_offset.x() + x * self.zoom
        v = self.pan_offset.y() - y * self.zoom
        return QPointF(u, v)

    def screen_to_world(self, u: float, v: float) -> Tuple[float, float]:
        """Convert screen pixels to world coordinates (where +Y is UP)."""
        x = (u - self.pan_offset.x()) / self.zoom
        y = (self.pan_offset.y() - v) / self.zoom
        return x, y

    def reset_view(self):
        """Reset zoom and center view around origin or points."""
        if not self.control_points:
            self.zoom = 1.0
            self.pan_offset = QPointF(self.width() / 2.0, self.height() / 2.0)
        else:
            xs = [p[0] for p in self.control_points]
            ys = [p[1] for p in self.control_points]
            min_x, max_x = min(xs), max(xs)
            min_y, max_y = min(ys), max(ys)
            w = max(100.0, max_x - min_x)
            h = max(100.0, max_y - min_y)
            center_x = (min_x + max_x) / 2.0
            center_y = (min_y + max_y) / 2.0

            margin = 80.0
            zoom_x = (self.width() - margin * 2) / w
            zoom_y = (self.height() - margin * 2) / h
            self.zoom = max(0.2, min(zoom_x, zoom_y, 3.0))

            self.pan_offset = QPointF(
                self.width() / 2.0 - center_x * self.zoom,
                self.height() / 2.0 + center_y * self.zoom
            )
        self.update()

    # -------------------------------------------------------------
    # State & Data Setters
    # -------------------------------------------------------------
    def set_control_points(self, points: List[Tuple[float, float]]):
        self.control_points = list(points)
        self.points_changed.emit()
        self.update()

    def set_spline_curve(self, curve: np.ndarray):
        self.spline_curve_points = curve
        self.update()

    def set_fourier_series(self, fs: Optional[FourierSeries2D]):
        self.fourier_series = fs
        self.update_reconstruction()
        self.update()

    def set_num_epicycles(self, count: int):
        self.num_epicycles_to_draw = count
        self.update_reconstruction()
        self.update()

    def update_reconstruction(self):
        if self.fourier_series is not None and len(self.fourier_series.sorted_epicycles) > 0:
            self.reconstructed_curve = self.fourier_series.evaluate_reconstruction(
                self.num_epicycles_to_draw, num_points=600
            )
        else:
            self.reconstructed_curve = np.zeros((0, 2))

    def set_time(self, t: float):
        self.current_t = t % 1.0
        self.update()

    # -------------------------------------------------------------
    # Paint Event
    # -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)

        # Background
        painter.fillRect(self.rect(), QColor("#090d16"))

        # 1. Grid & Axes
        if self.show_grid:
            self._draw_grid(painter)
        if self.show_axes:
            self._draw_axes(painter)

        # 2. Control Polygon & Original Spline
        if self.show_control_polygon and len(self.control_points) > 1:
            self._draw_control_polygon(painter)

        if self.show_original_spline and len(self.spline_curve_points) > 1:
            self._draw_spline_curve(painter)

        # 3. Fourier Reconstructed Static Path
        if self.show_reconstructed_curve and len(self.reconstructed_curve) > 1:
            self._draw_reconstructed_curve(painter)

        # 4. Animated Epicycles & Pen Tip
        if self.fourier_series is not None and len(self.fourier_series.sorted_epicycles) > 0:
            self._draw_epicycles(painter)

        # 5. Freehand in-progress drawing
        if self.is_freehand_drawing and len(self.freehand_raw_points) > 1:
            self._draw_freehand_preview(painter)

        # 6. Control Points on top
        if self.show_control_points:
            self._draw_control_points(painter)

        # 7. Coordinate overlay info
        self._draw_overlay_hud(painter)

    def _draw_grid(self, painter: QPainter):
        # Calculate optimal grid spacing
        # Target roughly 50 to 120 pixels per grid step
        target_step_px = 60.0
        world_step = target_step_px / self.zoom

        # Round to 1, 2, 5 * 10^k
        power = math.floor(math.log10(world_step))
        fraction = world_step / (10 ** power)
        if fraction < 1.5:
            step = 1.0 * (10 ** power)
        elif fraction < 3.5:
            step = 2.0 * (10 ** power)
        elif fraction < 7.5:
            step = 5.0 * (10 ** power)
        else:
            step = 10.0 * (10 ** power)

        # Visible world boundaries
        w_left, w_top = self.screen_to_world(0, 0)
        w_right, w_bottom = self.screen_to_world(self.width(), self.height())

        x_start = math.floor(w_left / step) * step
        x_end = math.ceil(w_right / step) * step
        y_start = math.floor(w_bottom / step) * step
        y_end = math.ceil(w_top / step) * step

        grid_pen = QPen(QColor(30, 41, 59, 140), 1, Qt.DotLine)
        painter.setPen(grid_pen)

        font = QFont("Helvetica Neue", 9)
        painter.setFont(font)
        text_pen = QPen(QColor(100, 116, 139, 160))

        # Vertical grid lines
        x = x_start
        while x <= x_end:
            p1 = self.world_to_screen(x, w_bottom)
            p2 = self.world_to_screen(x, w_top)
            painter.setPen(grid_pen)
            painter.drawLine(p1, p2)
            if abs(x) > 1e-6:
                painter.setPen(text_pen)
                lbl_pos = self.world_to_screen(x, 0)
                # Clamp label to screen bounds
                y_lbl = min(max(lbl_pos.y() + 14, 18), self.height() - 8)
                painter.drawText(int(lbl_pos.x() + 4), int(y_lbl), f"{x:g}")
            x += step

        # Horizontal grid lines
        y = y_start
        while y <= y_end:
            p1 = self.world_to_screen(w_left, y)
            p2 = self.world_to_screen(w_right, y)
            painter.setPen(grid_pen)
            painter.drawLine(p1, p2)
            if abs(y) > 1e-6:
                painter.setPen(text_pen)
                lbl_pos = self.world_to_screen(0, y)
                x_lbl = min(max(lbl_pos.x() + 6, 8), self.width() - 40)
                painter.drawText(int(x_lbl), int(lbl_pos.y() - 3), f"{y:g}")
            y += step

    def _draw_axes(self, painter: QPainter):
        origin = self.world_to_screen(0, 0)
        axis_pen = QPen(QColor(71, 85, 105, 200), 1.5, Qt.SolidLine)
        painter.setPen(axis_pen)

        # X Axis
        painter.drawLine(QPointF(0, origin.y()), QPointF(self.width(), origin.y()))
        # Y Axis
        painter.drawLine(QPointF(origin.x(), 0), QPointF(origin.x(), self.height()))

        # Origin marker
        painter.setBrush(QBrush(QColor(56, 189, 248, 180)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(origin, 4, 4)

        # Label (0,0)
        painter.setPen(QColor(148, 163, 184))
        painter.drawText(int(origin.x() + 6), int(origin.y() + 14), "(0, 0)")

    def _draw_control_polygon(self, painter: QPainter):
        poly_pen = QPen(QColor(148, 163, 184, 80), 1.2, Qt.DashLine)
        painter.setPen(poly_pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        p0 = self.world_to_screen(*self.control_points[0])
        path.moveTo(p0)
        for pt in self.control_points[1:]:
            path.lineTo(self.world_to_screen(*pt))
        if self.is_closed and len(self.control_points) > 2:
            path.lineTo(p0)
        painter.drawPath(path)

    def _draw_spline_curve(self, painter: QPainter):
        curve_pen = QPen(QColor(14, 165, 233, 200), 2.2, Qt.SolidLine)  # Cyan
        painter.setPen(curve_pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        p0 = self.world_to_screen(self.spline_curve_points[0, 0], self.spline_curve_points[0, 1])
        path.moveTo(p0)
        for i in range(1, len(self.spline_curve_points)):
            path.lineTo(self.world_to_screen(self.spline_curve_points[i, 0], self.spline_curve_points[i, 1]))
        if self.is_closed and len(self.spline_curve_points) > 2:
            path.lineTo(p0)
        painter.drawPath(path)

    def _draw_reconstructed_curve(self, painter: QPainter):
        # Ghost / Reference full Fourier curve
        recon_pen = QPen(QColor(234, 179, 8, 130), 1.5, Qt.DashLine)  # Amber gold
        painter.setPen(recon_pen)
        painter.setBrush(Qt.NoBrush)

        path = QPainterPath()
        p0 = self.world_to_screen(self.reconstructed_curve[0, 0], self.reconstructed_curve[0, 1])
        path.moveTo(p0)
        for i in range(1, len(self.reconstructed_curve)):
            path.lineTo(self.world_to_screen(self.reconstructed_curve[i, 0], self.reconstructed_curve[i, 1]))
        if self.is_closed:
            path.lineTo(p0)
        painter.drawPath(path)

    def _draw_epicycles(self, painter: QPainter):
        if self.fourier_series is None:
            return

        centers, radii, tip = self.fourier_series.evaluate_chain(
            self.current_t, self.num_epicycles_to_draw
        )
        if not centers:
            return

        active_eps = self.fourier_series.get_active_epicycles(self.num_epicycles_to_draw)
        screen_centers = [self.world_to_screen(c[0], c[1]) for c in centers]
        screen_tip = self.world_to_screen(tip[0], tip[1])

        # Draw Circles & Vectors
        circle_pen = QPen(QColor(168, 85, 247, 50), 1.2, Qt.SolidLine)
        vector_pen = QPen(QColor(192, 132, 252, 200), 1.8, Qt.SolidLine)

        num_c = len(screen_centers)
        for i in range(num_c):
            c_screen = screen_centers[i]
            r_world = radii[i]
            r_screen = r_world * self.zoom

            # Next center or tip is the target of the vector
            next_screen = screen_centers[i + 1] if i + 1 < num_c else screen_tip

            # Circle
            if self.show_epicycle_circles and r_screen > 1.5:
                # Fade smaller circles slightly
                alpha = int(max(30, min(140, 60 + 80 * (1.0 - i / max(1, num_c)))))
                circle_pen.setColor(QColor(168, 85, 247, alpha))
                painter.setPen(circle_pen)
                painter.setBrush(Qt.NoBrush)
                painter.drawEllipse(c_screen, r_screen, r_screen)

            # Vector arrow from this center to next center
            if self.show_epicycle_vectors and r_screen > 1.0:
                painter.setPen(vector_pen)
                painter.drawLine(c_screen, next_screen)

        # Real-time trail (from t=0 up to current t)
        if self.show_trail and len(self.reconstructed_curve) > 2:
            trail_len = int(len(self.reconstructed_curve) * self.current_t)
            if trail_len > 1:
                trail_pen = QPen(QColor(250, 204, 21, 230), 2.8, Qt.SolidLine)  # Glowing yellow
                painter.setPen(trail_pen)
                painter.setBrush(Qt.NoBrush)
                trail_path = QPainterPath()
                t0 = self.world_to_screen(self.reconstructed_curve[0, 0], self.reconstructed_curve[0, 1])
                trail_path.moveTo(t0)
                for j in range(1, trail_len):
                    trail_path.lineTo(self.world_to_screen(self.reconstructed_curve[j, 0], self.reconstructed_curve[j, 1]))
                trail_path.lineTo(screen_tip)
                painter.drawPath(trail_path)

        # Pen Tip
        if self.show_pen_tip:
            # Outer glow
            painter.setBrush(QBrush(QColor(250, 204, 21, 80)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(screen_tip, 8, 8)

            # Center dot
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(screen_tip, 3.5, 3.5)

    def _draw_control_points(self, painter: QPainter):
        font = QFont("Helvetica Neue", 9, QFont.Bold)
        painter.setFont(font)

        for i, (wx, wy) in enumerate(self.control_points):
            sp = self.world_to_screen(wx, wy)
            is_hovered = (i == self.hovered_point_idx)
            is_selected = (i == self.selected_point_idx)

            # Outer radius
            r = 7 if (is_hovered or is_selected) else 5.5

            if is_selected:
                fill_color = QColor(251, 191, 36)  # Amber
                border_color = QColor(255, 255, 255)
            elif is_hovered:
                fill_color = QColor(244, 63, 94)   # Rose red hover
                border_color = QColor(255, 255, 255)
            else:
                fill_color = QColor(225, 29, 72)   # Rose red
                border_color = QColor(255, 255, 255, 200)

            painter.setBrush(QBrush(fill_color))
            painter.setPen(QPen(border_color, 1.8))
            painter.drawEllipse(sp, r, r)

            # Point label
            painter.setPen(QColor(241, 245, 249))
            painter.drawText(int(sp.x() + r + 3), int(sp.y() - r + 3), f"P{i}")

            if is_hovered:
                # Show coordinates tooltip near hovered point
                coord_text = f"({wx:.1f}, {wy:.1f})"
                painter.setPen(QColor(56, 189, 248))
                painter.drawText(int(sp.x() + r + 3), int(sp.y() + r + 11), coord_text)

    def _draw_freehand_preview(self, painter: QPainter):
        pen = QPen(QColor(244, 63, 94, 200), 2.0, Qt.DotLine)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        path = QPainterPath()
        p0 = self.world_to_screen(*self.freehand_raw_points[0])
        path.moveTo(p0)
        for pt in self.freehand_raw_points[1:]:
            path.lineTo(self.world_to_screen(*pt))
        painter.drawPath(path)

    def _draw_overlay_hud(self, painter: QPainter):
        font = QFont("Menlo", 9)
        painter.setFont(font)
        painter.setPen(QColor(148, 163, 184, 180))

        # Bottom-left HUD info
        hud_lines = [
            f"Zoom: {int(self.zoom * 100)}%",
            f"Punkte: {len(self.control_points)}",
            f"Epizyklen: {self.num_epicycles_to_draw}",
            f"t = {self.current_t:.3f} ({int(self.current_t * 360)}°)",
        ]
        if self.freehand_mode:
            hud_lines.append("MODUS: Freihand-Zeichnen (Maus gedrückt halten)")

        y = self.height() - 15 - len(hud_lines) * 16
        for line in hud_lines:
            painter.drawText(15, y, line)
            y += 16

    # -------------------------------------------------------------
    # Mouse & Keyboard Event Handlers
    # -------------------------------------------------------------
    def _find_point_near(self, screen_pos: QPointF, max_dist_px: float = 14.0) -> Optional[int]:
        for i, (wx, wy) in enumerate(self.control_points):
            sp = self.world_to_screen(wx, wy)
            dist = math.hypot(sp.x() - screen_pos.x(), sp.y() - screen_pos.y())
            if dist <= max_dist_px:
                return i
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        world_x, world_y = self.screen_to_world(pos.x(), pos.y())

        # Middle click or Space+Left click: Pan
        if event.button() == Qt.MiddleButton or (event.button() == Qt.LeftButton and self.is_space_pressed):
            self.is_panning = True
            self.pan_start = pos
            self.setCursor(Qt.ClosedHandCursor)
            return

        # Freehand sketch mode
        if self.freehand_mode and event.button() == Qt.LeftButton:
            self.is_freehand_drawing = True
            self.freehand_raw_points = [(world_x, world_y)]
            self.update()
            return

        # Check if clicking on an existing point
        point_idx = self._find_point_near(pos)

        if event.button() == Qt.LeftButton:
            if point_idx is not None:
                # Start dragging existing point
                self.selected_point_idx = point_idx
                self.setCursor(Qt.ClosedHandCursor)
            else:
                # Add a new point at click location
                self.control_points.append((round(world_x, 1), round(world_y, 1)))
                self.selected_point_idx = len(self.control_points) - 1
                self.points_changed.emit()
            self.update()

        elif event.button() == Qt.RightButton:
            if point_idx is not None:
                # Delete clicked point
                self.control_points.pop(point_idx)
                self.selected_point_idx = None
                self.hovered_point_idx = None
                self.points_changed.emit()
                self.update()
            else:
                # Pan with right drag on empty space
                self.is_panning = True
                self.pan_start = pos
                self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        pos = event.pos()
        world_x, world_y = self.screen_to_world(pos.x(), pos.y())
        self.cursor_moved.emit(world_x, world_y)

        # Pan update
        if self.is_panning:
            delta = pos - self.pan_start
            self.pan_offset += delta
            self.pan_start = pos
            self.update()
            return

        # Freehand drawing update
        if self.is_freehand_drawing:
            # Only add if moved enough distance
            last_p = self.freehand_raw_points[-1]
            if math.hypot(world_x - last_p[0], world_y - last_p[1]) > 5.0 / self.zoom:
                self.freehand_raw_points.append((world_x, world_y))
                self.update()
            return

        # Dragging control point
        if self.selected_point_idx is not None and (event.buttons() & Qt.LeftButton):
            self.control_points[self.selected_point_idx] = (round(world_x, 1), round(world_y, 1))
            self.points_changed.emit()
            self.update()
            return

        # Hover detection
        old_hover = self.hovered_point_idx
        self.hovered_point_idx = self._find_point_near(pos)
        if self.hovered_point_idx != old_hover:
            if self.hovered_point_idx is not None:
                self.setCursor(Qt.PointingHandCursor)
            elif not self.is_space_pressed:
                self.setCursor(Qt.CrossCursor if not self.freehand_mode else Qt.ArrowCursor)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.is_panning:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)

        if self.is_freehand_drawing:
            self.is_freehand_drawing = False
            # Downsample freehand points into smooth control points
            if len(self.freehand_raw_points) >= 4:
                # Resample into e.g. 16-24 control points
                raw_arr = np.array(self.freehand_raw_points)
                try:
                    from core.splines import resample_polyline
                except (ImportError, ValueError):
                    from ..core.splines import resample_polyline
                sampled = resample_polyline(raw_arr, num_samples=18, closed=self.is_closed)
                self.control_points = [(round(p[0], 1), round(p[1], 1)) for p in sampled]
                self.points_changed.emit()
            self.freehand_raw_points = []
            self.update()

        if self.selected_point_idx is not None:
            self.selected_point_idx = None
            self.setCursor(Qt.PointingHandCursor if self.hovered_point_idx is not None else Qt.CrossCursor)
            self.update()

    def wheelEvent(self, event):
        # Zoom centered on cursor position
        pos = event.pos()
        old_world_x, old_world_y = self.screen_to_world(pos.x(), pos.y())

        delta = event.angleDelta().y()
        zoom_factor = 1.15 if delta > 0 else (1.0 / 1.15)
        new_zoom = max(0.05, min(self.zoom * zoom_factor, 20.0))

        self.zoom = new_zoom
        # Adjust pan_offset so that the world point under cursor remains under cursor
        self.pan_offset = QPointF(
            pos.x() - old_world_x * self.zoom,
            pos.y() + old_world_y * self.zoom
        )
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.is_space_pressed = True
            self.setCursor(Qt.OpenHandCursor)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.is_space_pressed = False
            self.setCursor(Qt.CrossCursor)
        super().keyReleaseEvent(event)
