"""
Modern dark macOS-inspired theme styling for FourierSplineStudio.
"""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #16161a;
    color: #fffffe;
}

QWidget {
    font-family: "Helvetica Neue", Arial;
    font-size: 13px;
    color: #e2e8f0;
}

/* ScrollBars */
QScrollBar:vertical {
    background: #18181b;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #3f3f46;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #71717a;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #27272a;
    background: #18181b;
    border-radius: 8px;
    padding: 2px;
}
QTabBar::tab {
    background: #27272a;
    color: #a1a1aa;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 3px;
    font-weight: 500;
}
QTabBar::tab:selected {
    background: #0284c7;
    color: #ffffff;
    font-weight: bold;
}
QTabBar::tab:hover:!selected {
    background: #3f3f46;
    color: #f4f4f5;
}

/* GroupBoxes */
QGroupBox {
    font-weight: bold;
    border: 1px solid #334155;
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 8px 8px 8px;
    background-color: #1e293b;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    color: #38bdf8;
}

/* PushButtons */
QPushButton {
    background-color: #334155;
    color: #f8fafc;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 500;
}
QPushButton:hover {
    background-color: #475569;
    border-color: #64748b;
}
QPushButton:pressed {
    background-color: #1e293b;
}
QPushButton:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
    color: #ffffff;
}

QPushButton#playButton {
    background-color: #059669;
    border-color: #10b981;
    font-weight: bold;
    font-size: 14px;
    min-height: 28px;
}
QPushButton#playButton:hover {
    background-color: #10b981;
}

QPushButton#recordButton {
    background-color: #be123c;
    border-color: #f43f5e;
}
QPushButton#recordButton:hover {
    background-color: #e11d48;
}

/* ComboBox */
QComboBox {
    background-color: #1e293b;
    border: 1px solid #475569;
    border-radius: 6px;
    padding: 5px 10px;
    color: #f8fafc;
}
QComboBox:hover {
    border-color: #38bdf8;
}
QComboBox::drop-down {
    border: none;
    width: 20px;
}
QComboBox QAbstractItemView {
    background-color: #1e293b;
    border: 1px solid #475569;
    selection-background-color: #0284c7;
    selection-color: white;
    color: #f8fafc;
}

/* Sliders */
QSlider::groove:horizontal {
    border: none;
    height: 6px;
    background: #334155;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #38bdf8;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #f8fafc;
    border: 2px solid #0284c7;
    width: 16px;
    margin-top: -5px;
    margin-bottom: -5px;
    border-radius: 8px;
}
QSlider::handle:horizontal:hover {
    background: #38bdf8;
    border-color: #ffffff;
}

/* CheckBox */
QCheckBox {
    spacing: 7px;
    color: #cbd5e1;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #64748b;
    background-color: #1e293b;
}
QCheckBox::indicator:checked {
    background-color: #0284c7;
    border-color: #38bdf8;
    image: none;
}
QCheckBox::indicator:hover {
    border-color: #38bdf8;
}

/* TextEdit / Code display */
QTextEdit, QPlainTextEdit {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: Menlo, Monaco, "Courier New", monospace;
    font-size: 12px;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px;
}

/* TableView */
QTableWidget {
    background-color: #0f172a;
    alternate-background-color: #1e293b;
    gridline-color: #334155;
    color: #e2e8f0;
    border: 1px solid #334155;
    border-radius: 6px;
}
QHeaderView::section {
    background-color: #1e293b;
    color: #38bdf8;
    font-weight: bold;
    padding: 6px;
    border: 1px solid #334155;
}
QTableWidget::item:selected {
    background-color: #0284c7;
    color: white;
}

/* Labels */
QLabel {
    color: #e2e8f0;
}
QLabel#metricLabel {
    color: #a5f3fc;
    font-family: Menlo, Monaco, monospace;
    font-size: 12px;
}
"""
