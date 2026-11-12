# 🌀 Fourier & Spline Studio

Ein interaktives Python-Tool mit moderner macOS-Benutzeroberfläche zum Zeichnen und Modifizieren von **Splines auf einer 2D-XY-Ebene** sowie zur **analytischen Funktionsausgabe über Fourier-Epizyklen** (im Stil von 3Blue1Brown).

---

## ✨ Features im Überblick

### 1. Interaktives Zeichnen auf der XY-Ebene
- **Koordinatensystem**: Echtes kartesisches Koordinatensystem (mathematisch $+Y$ nach oben, $+X$ nach rechts), mit adaptivem Gitter, Achsenskalierung und Ursprungsanzeige $(0, 0)$.
- **Spline-Algorithmen wählbar**:
  - **Catmull-Rom Spline**: Geht exakt und glatt durch alle gesetzten Kontrollpunkte ($C^1$).
  - **Kubischer Spline**: $C^2$-stetige glatte Interpolation mit minimierter Krümmung.
  - **Bézier-Spline**: Glatte kubische Bézier-Segmente ($G^1$).
  - **B-Spline**: Gleichmäßiger kubischer B-Spline zur Approximation des Kontrollpolygons.
  - **Polygonzug (Linear)**: Geradlinige Verbindungen.
- **Interaktion**:
  - **Linksklick auf leere Fläche**: Neuen Kontrollpunkt hinzufügen.
  - **Linksklick auf Punkt & Ziehen**: Punkt verschieben mit Live-Aktualisierung der Kurve.
  - **Rechtsklick auf Punkt**: Kontrollpunkt löschen.
  - **Freihand-Modus**: Maus gedrückt halten, um frei eine Kurve zu skizzieren; wird automatisch in einen glatten Spline umgerechnet!
  - **Mausrad**: Stufenloser Zoom zentriert am Mauszeiger.
  - **Leertaste + Ziehen** oder **Mittelklick / Rechtsklick ziehen**: Leinwand verschieben (Pan).
- **Vorlagen (Presets)**:
  - Herzform, Unendlichkeitssymbol (Lemniskate), 5-Zack-Stern, Kleeblatt (Trefoil), Kreis, S-Welle.

---

### 2. Fourier-Epizyklen (3Blue1Brown-Stil)
- **Diskrete & Kontinuierliche Fourier-Transformation (DFT)** auf der komplexen Ebene:
  $$z(t) = x(t) + i \cdot y(t) = \sum_{k} c_k \, e^{i \cdot 2\pi k t}$$
- **Epizyklen-Kette**: Jede Frequenz $k$ wird als rotierender Vektor dargestellt:
  - Radius $R_k = |c_k|$
  - Rotationsfrequenz $\omega_k = 2\pi k$
  - Phasenverschiebung $\phi_k = \operatorname{arg}(c_k)$
- **Interaktive Steuerung**:
  - Regler für die **Anzahl der Epizyklen (Harmonische $N$)**: Von 1 bis 120+. Beobachte live, wie höhere Harmonische feine Details und Kanten der Kurve rekonstruieren!
  - **Echtzeit-Fehleranzeige**: Mittlerer und maximaler Approximationsfehler in Pixeln ($\Delta L_{avg}, \Delta L_{max}$) sowie Anteil der harmonischen Energie.
  - **Live-Animation**: Start/Pause, Geschwindigkeitsregler ($0.1\times$ bis $4.0\times$) und Zeitschieberegler $t \in [0, 1]$ ($0^\circ$ bis $360^\circ$).
  - **Ebenen ein/ausblenden**: Epizyklen-Kreise, Vektorpfeile, Reconstruktionspfad, Original-Spline, Kontrollnetz, Stift-Spur.

---

### 3. Mathematische Funktionsausgabe & Export
Das Tool erzeugt die mathematische Kurvendarstellung in mehreren Formaten:

1. **Epizyklen Komplexformel**:
   $$z(t) = c_0 + \sum_{k} R_k \cdot e^{i \cdot (2\pi f_k t + \phi_k)}$$
2. **Kartesisch-trigonometrische Funktionen**:
   $$x(t) = \dots + \sum_{k} R_k \cdot \cos(2\pi f_k t + \phi_k)$$
   $$y(t) = \dots + \sum_{k} R_k \cdot \sin(2\pi f_k t + \phi_k)$$
3. **Ausführbarer Python-Code**:
   Vollständiges Skript mit `numpy`-Vektorisierung und optionalem `matplotlib`-Plot, direkt per Klick kopierbar oder als `.py` speicherbar.
4. **LaTeX-Gleichungen**:
   Formatiert mit `\begin{aligned}` für wissenschaftliche Dokumente oder Notizen.
5. **Desmos Graphing Calculator**:
   Parametrischer Ausdruck `(X(t), Y(t))` für direkte Eingabe auf [desmos.com](https://www.desmos.com/calculator).
6. **JavaScript-Funktion**:
   Web-fertige Funktion für HTML5 Canvas oder WebGL.
7. **Harmonische-Spektrum-Tabelle**:
   Tabellarische Aufschlüsselung aller Frequenzen $k$, Amplituden $R_k$, Phasenwinkel $\phi_k$ (in Radiant und Grad) und ihres relativen Energiebeitrags.

---

## 🚀 Schnellstart auf dem Mac

### Option 1: Per Doppelklick
Einfach die Datei **`start.command`** im Finder doppelt anklicken!

### Option 2: Im Terminal
```bash
cd FourierSplineStudio
./run.sh
```

Das Skript `run.sh` erkennt automatisch vorhandene Python-Umgebungen mit `PyQt5` und `numpy` (wie z.B. `.venv-1`) oder richtet bei Bedarf eine lokale virtuelle Umgebung ein.

---

## ⌨️ Tasten- & Maus-Steuerung

| Aktion | Steuerung |
| :--- | :--- |
| **Neuen Punkt setzen** | Linksklick auf freie Fläche |
| **Punkt verschieben** | Linksklick auf Punkt gedrückt halten & ziehen |
| **Punkt löschen** | Rechtsklick auf Punkt |
| **Zoomen** | Mausrad vor / zurück |
| **Verschieben (Pan)** | Leertaste halten + Ziehen **oder** Mittelklick ziehen **oder** Rechtsklick auf freie Fläche ziehen |
| **Freihand zeichnen** | "Freihand Zeichnen" aktivieren $\to$ Linke Maustaste gedrückt halten |
| **Ansicht einpassen** | Button "Ansicht anpassen" |

---

## 📁 Projektstruktur

```
FourierSplineStudio/
├── main.py              # Einstiegspunkt der Anwendung
├── run.sh               # Ausführbares Startskript
├── start.command        # Doppelklick-Starter für macOS Finder
├── requirements.txt     # Python-Abhängigkeiten (PyQt5, numpy)
├── core/
│   ├── splines.py       # Spline-Berechnung (Catmull-Rom, B-Spline, Bézier, Kubisch)
│   ├── fourier.py       # DFT, Epizyklen-Kette & Evaluierung
│   ├── export_math.py   # Formelgeneratoren (LaTeX, Python, Desmos, etc.)
│   └── presets.py       # Vordefinierte Kurvenformen (Herz, Lemniskate, Stern...)
└── ui/
    ├── canvas.py        # Interaktive QPainter XY-Zeichenebene & Animation
    ├── control_panel.py # Bedienelemente für Splines, Epizyklen & Animation
    ├── formula_view.py  # Anzeige der mathematischen Funktionen mit Kopierfunktion
    ├── harmonics_view.py# Spektrum-Tabelle aller Harmonischen
    ├── main_window.py   # Hauptfenster
    └── style.py         # macOS Dark-Theme Styling
```
