#!/usr/bin/env python3
"""
Fourier & Spline Studio
An interactive tool for designing 2D splines on an XY plane and synthesizing
their analytical curve functions via Fourier Epicycles.
"""

import sys
import os

# Ensure package directory is in sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow
from ui.style import DARK_THEME_QSS


def main():
    # Enable high-DPI scaling for crisp macOS Retina rendering
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("FourierSplineStudio")
    app.setStyleSheet(DARK_THEME_QSS)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
