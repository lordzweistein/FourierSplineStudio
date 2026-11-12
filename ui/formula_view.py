"""
Mathematical Formulas & Function Output View.
Displays Fourier Epicycles analytical formulas, Cartesian functions,
LaTeX, Python code, and Desmos parametric equations with one-click copy.
"""

from typing import List
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QComboBox, QLabel, QFileDialog, QApplication
)
from PyQt5.QtCore import Qt, QTimer

try:
    from core.fourier import Epicycle
    from core.export_math import (
        generate_epicycles_complex_formula,
        generate_cartesian_formulas,
        generate_latex_formula,
        generate_python_code,
        generate_desmos_syntax,
        generate_javascript_code
    )
except (ImportError, ValueError):
    from ..core.fourier import Epicycle
    from ..core.export_math import (
        generate_epicycles_complex_formula,
        generate_cartesian_formulas,
        generate_latex_formula,
        generate_python_code,
        generate_desmos_syntax,
        generate_javascript_code
    )


class FormulaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_epicycles: List[Epicycle] = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header with format dropdown and action buttons
        header_layout = QHBoxLayout()

        lbl_format = QLabel("Ausgabe-Format:")
        lbl_format.setStyleSheet("font-weight: bold; color: #38bdf8;")
        self.combo_format = QComboBox()
        self.combo_format.addItem("Epizyklen Komplex (z(t) = Σ R·e^(i·ωt))")
        self.combo_format.addItem("Kartesisch Trigonometrisch (x(t), y(t))")
        self.combo_format.addItem("Python Script (Eigenständig & Ausführbar)")
        self.combo_format.addItem("LaTeX Formel (Mathematik-Code)")
        self.combo_format.addItem("Desmos Graphing Calculator Syntax")
        self.combo_format.addItem("JavaScript Funktion")
        self.combo_format.currentIndexChanged.connect(self._refresh_content)

        self.btn_copy = QPushButton("📋 In Zwischenablage kopieren")
        self.btn_copy.clicked.connect(self._copy_to_clipboard)

        self.btn_save = QPushButton("💾 Als Datei speichern...")
        self.btn_save.clicked.connect(self._save_to_file)

        header_layout.addWidget(lbl_format)
        header_layout.addWidget(self.combo_format, 1)
        header_layout.addWidget(self.btn_copy)
        header_layout.addWidget(self.btn_save)
        layout.addLayout(header_layout)

        # Formula text display
        self.text_editor = QTextEdit()
        self.text_editor.setReadOnly(True)
        self.text_editor.setLineWrapMode(QTextEdit.NoWrap)
        layout.addWidget(self.text_editor)

        # Quick tip bar at bottom
        self.lbl_tip = QLabel("Tipp: Das Intervall für t ist normalisiert auf [0, 1] für einen vollständigen Umlauf.")
        self.lbl_tip.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(self.lbl_tip)

    def set_epicycles(self, epicycles: List[Epicycle]):
        self.current_epicycles = list(epicycles)
        self._refresh_content()

    def _refresh_content(self):
        idx = self.combo_format.currentIndex()
        if not self.current_epicycles:
            self.text_editor.setPlainText("Zeichne zuerst eine Kurve auf der XY-Ebene, um die Formeln zu generieren.")
            return

        if idx == 0:
            # Epizyklen Komplex
            content = generate_epicycles_complex_formula(self.current_epicycles)
        elif idx == 1:
            # Kartesisch
            parts = generate_cartesian_formulas(self.current_epicycles)
            content = f"{parts['x']}\n\n{parts['y']}"
        elif idx == 2:
            # Python Script
            content = generate_python_code(self.current_epicycles)
        elif idx == 3:
            # LaTeX
            content = generate_latex_formula(self.current_epicycles)
        elif idx == 4:
            # Desmos
            content = generate_desmos_syntax(self.current_epicycles)
        elif idx == 5:
            # JavaScript
            content = generate_javascript_code(self.current_epicycles)
        else:
            content = ""

        self.text_editor.setPlainText(content)

    def _copy_to_clipboard(self):
        text = self.text_editor.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            self.btn_copy.setText("✓ Kopiert!")
            self.btn_copy.setStyleSheet("background-color: #059669; color: white;")
            QTimer.singleShot(1500, self._reset_copy_btn)

    def _reset_copy_btn(self):
        self.btn_copy.setText("📋 In Zwischenablage kopieren")
        self.btn_copy.setStyleSheet("")

    def _save_to_file(self):
        text = self.text_editor.toPlainText()
        if not text:
            return

        idx = self.combo_format.currentIndex()
        if idx == 2:
            filt = "Python Files (*.py);;Text Files (*.txt);;All Files (*)"
            default_name = "fourier_curve.py"
        elif idx == 3:
            filt = "LaTeX Files (*.tex);;Text Files (*.txt);;All Files (*)"
            default_name = "fourier_curve.tex"
        elif idx == 5:
            filt = "JavaScript Files (*.js);;Text Files (*.txt);;All Files (*)"
            default_name = "fourier_curve.js"
        else:
            filt = "Text Files (*.txt);;All Files (*)"
            default_name = "fourier_function.txt"

        path, _ = QFileDialog.getSaveFileName(self, "Formel exportieren", default_name, filt)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
