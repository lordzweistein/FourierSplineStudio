"""
Fourier Harmonics & Epicycles Spectrum Table.
Inspect individual rotating circles, their frequencies, radii, phases, and energy.
"""

import math
from typing import List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt

try:
    from core.fourier import Epicycle
except (ImportError, ValueError):
    from ..core.fourier import Epicycle


class HarmonicsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Header info
        top_row = QHBoxLayout()
        self.lbl_summary = QLabel("Keine Epizyklen geladen.")
        self.lbl_summary.setStyleSheet("font-weight: bold; color: #38bdf8;")
        top_row.addWidget(self.lbl_summary)
        top_row.addStretch()
        layout.addLayout(top_row)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Rang", "Frequenz (k)", "Radius |c_k|", "Phase (rad)", "Phase (°)", "Energie (%)"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)

    def set_epicycles(self, epicycles: List[Epicycle]):
        self.table.setRowCount(0)
        if not epicycles:
            self.lbl_summary.setText("Keine Epizyklen vorhanden.")
            return

        self.table.setRowCount(len(epicycles))
        total_energy = sum(ep.radius ** 2 for ep in epicycles)

        for i, ep in enumerate(epicycles):
            deg = math.degrees(ep.phase)
            energy_pct = (ep.radius ** 2 / total_energy * 100.0) if total_energy > 0 else 0.0

            items = [
                QTableWidgetItem(f"#{i+1}"),
                QTableWidgetItem(f"{ep.freq:+d}" if ep.freq != 0 else "0 (DC)"),
                QTableWidgetItem(f"{ep.radius:.4f}"),
                QTableWidgetItem(f"{ep.phase:+.4f}"),
                QTableWidgetItem(f"{deg:+.1f}°"),
                QTableWidgetItem(f"{energy_pct:.2f}%"),
            ]

            for col_idx, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, col_idx, item)

        self.lbl_summary.setText(
            f"Epizyklen gesamt: {len(epicycles)} | Dominanter Kreis: Radius = {epicycles[0].radius:.2f} (k={epicycles[0].freq})"
        )
