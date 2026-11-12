"""
Mathematical Formula Formatter and Exporter.
Generates clean, readable mathematical functions from Epicycles and Splines:
- Complex exponential Fourier series
- Real trigonometric Cartesian form (x(t), y(t))
- LaTeX equations
- Runnable Python function
- Desmos / GeoGebra parametric curve syntax
- JavaScript / GLSL code
"""

import math
from typing import List
from .fourier import Epicycle, FourierSeries2D


def format_number(val: float, precision: int = 4) -> str:
    """Format float cleanly, stripping trailing zeros."""
    if abs(val) < 1e-9:
        return "0"
    s = f"{val:.{precision}f}".rstrip("0").rstrip(".")
    return s


def generate_epicycles_complex_formula(epicycles: List[Epicycle], precision: int = 4) -> str:
    """
    Returns string: z(t) = sum R_k * exp(i*(2*pi*f_k*t + phi_k))
    """
    if not epicycles:
        return "z(t) = 0"

    terms = []
    for ep in epicycles:
        r_str = format_number(ep.radius, precision)
        if ep.radius < 1e-6:
            continue

        if ep.freq == 0:
            # Constant DC term
            cx = format_number(ep.coeff.real, precision)
            cy = format_number(ep.coeff.imag, precision)
            sign_y = "+" if ep.coeff.imag >= 0 else "-"
            terms.append(f"({cx} {sign_y} {abs(float(cy))}i)")
            continue

        freq_str = f"2π·{ep.freq}·t" if ep.freq != 1 else "2π·t"
        if ep.freq < 0:
            freq_str = f"-2π·{abs(ep.freq)}·t"

        phi_val = ep.phase
        if abs(phi_val) > 1e-4:
            sign_phi = " + " if phi_val > 0 else " - "
            phi_str = f"{sign_phi}{format_number(abs(phi_val), precision)}"
        else:
            phi_str = ""

        terms.append(f"{r_str} · e^(i · ({freq_str}{phi_str}))")

    if not terms:
        return "z(t) = 0"

    return "z(t) =\n  " + "\n+ ".join(terms)


def generate_cartesian_formulas(epicycles: List[Epicycle], precision: int = 4) -> dict:
    """
    Returns dict with strings for x(t) and y(t).
    x(t) = sum R_k * cos(2*pi*f_k*t + phi_k)
    y(t) = sum R_k * sin(2*pi*f_k*t + phi_k)
    """
    if not epicycles:
        return {"x": "x(t) = 0", "y": "y(t) = 0"}

    x_terms = []
    y_terms = []

    for ep in epicycles:
        r_str = format_number(ep.radius, precision)
        if ep.radius < 1e-6:
            continue

        if ep.freq == 0:
            cx = format_number(ep.coeff.real, precision)
            cy = format_number(ep.coeff.imag, precision)
            x_terms.append(cx)
            y_terms.append(cy)
            continue

        freq_str = f"2π·{ep.freq}·t" if ep.freq != 1 else "2π·t"
        if ep.freq < 0:
            freq_str = f"-2π·{abs(ep.freq)}·t"

        phi_val = ep.phase
        if abs(phi_val) > 1e-4:
            sign_phi = " + " if phi_val > 0 else " - "
            phi_str = f"{sign_phi}{format_number(abs(phi_val), precision)}"
        else:
            phi_str = ""

        arg = f"{freq_str}{phi_str}"
        x_terms.append(f"{r_str} · cos({arg})")
        y_terms.append(f"{r_str} · sin({arg})")

    x_eq = "x(t) = " + " + ".join(x_terms) if x_terms else "x(t) = 0"
    y_eq = "y(t) = " + " + ".join(y_terms) if y_terms else "y(t) = 0"

    return {"x": x_eq, "y": y_eq}


def generate_latex_formula(epicycles: List[Epicycle], precision: int = 3, max_terms: int = 15) -> str:
    """
    Generates LaTeX representation of the Fourier Epicycle parametrization.
    """
    shown = epicycles[:max_terms]
    omitted = len(epicycles) - len(shown)

    terms = []
    for ep in shown:
        r_str = format_number(ep.radius, precision)
        if ep.radius < 1e-5:
            continue
        if ep.freq == 0:
            cx = format_number(ep.coeff.real, precision)
            cy = format_number(ep.coeff.imag, precision)
            sign_y = "+" if ep.coeff.imag >= 0 else "-"
            terms.append(f"\\left({cx} {sign_y} {abs(float(cy))} i\\right)")
            continue

        sign_k = "" if ep.freq >= 0 else "-"
        k_abs = abs(ep.freq)
        freq_part = f"2\\pi \\cdot {k_abs} t" if k_abs != 1 else "2\\pi t"
        if ep.freq < 0:
            freq_part = f"-{freq_part}"

        phi_val = ep.phase
        if abs(phi_val) > 1e-4:
            sign_phi = "+" if phi_val > 0 else "-"
            phi_str = f" {sign_phi} {format_number(abs(phi_val), precision)}"
        else:
            phi_str = ""

        terms.append(f"{r_str} \\, e^{{i \\left({freq_part}{phi_str}\\right)}}")

    latex_str = "\\begin{aligned}\n"
    latex_str += "z(t) &= "
    if terms:
        latex_str += " + \\\\\n  &\\quad ".join(terms)
        if omitted > 0:
            latex_str += f" + \\cdots \\quad (\\text{{{omitted} weitere Epizyklen}})"
    else:
        latex_str += "0"
    latex_str += "\n\\end{aligned}"
    return latex_str


def generate_python_code(epicycles: List[Epicycle], precision: int = 6) -> str:
    """
    Generates a standalone, executable Python script with function definition.
    """
    lines = [
        '"""',
        'Auto-generated Fourier Epicycles Function from FourierSplineStudio',
        f'Total Epicycles / Harmonics: {len(epicycles)}',
        'Parameter t runs from 0.0 to 1.0 (for one full loop)',
        '"""',
        'import math',
        'import numpy as np',
        '',
        '# Epicycle parameters: (freq, radius, phase_radians)',
        'EPICYCLES = ['
    ]

    for ep in epicycles:
        lines.append(f"    ({ep.freq:4d}, {ep.radius:.{precision}e}, {ep.phase:.{precision}f}),")

    lines.extend([
        ']',
        '',
        'def curve_point(t: float) -> tuple[float, float]:',
        '    """Evaluate (x, y) coordinates at parameter t in [0, 1]."""',
        '    x = 0.0',
        '    y = 0.0',
        '    two_pi = 2.0 * math.pi',
        '    for freq, radius, phase in EPICYCLES:',
        '        angle = two_pi * freq * t + phase',
        '        x += radius * math.cos(angle)',
        '        y += radius * math.sin(angle)',
        '    return (x, y)',
        '',
        'def sample_curve(num_points: int = 500) -> tuple[np.ndarray, np.ndarray]:',
        '    """Vectorized sampling of the entire Fourier curve."""',
        '    ts = np.linspace(0.0, 1.0, num_points, endpoint=True)',
        '    xs = np.zeros(num_points)',
        '    ys = np.zeros(num_points)',
        '    two_pi = 2.0 * np.pi',
        '    for freq, radius, phase in EPICYCLES:',
        '        angles = two_pi * freq * ts + phase',
        '        xs += radius * np.cos(angles)',
        '        ys += radius * np.sin(angles)',
        '    return xs, ys',
        '',
        'if __name__ == "__main__":',
        '    # Quick test point at t = 0.0',
        '    p0 = curve_point(0.0)',
        '    print(f"Curve at t=0: x={p0[0]:.4f}, y={p0[1]:.4f}")',
        '    try:',
        '        import matplotlib.pyplot as plt',
        '        xs, ys = sample_curve(1000)',
        '        plt.figure(figsize=(7, 7))',
        '        plt.plot(xs, ys, "b-", linewidth=2, label="Fourier Epicycles Curve")',
        '        plt.axis("equal")',
        '        plt.grid(True, alpha=0.3)',
        '        plt.title("Fourier Epicycles Reconstruction")',
        '        plt.legend()',
        '        plt.show()',
        '    except ImportError:',
        '        print("Matplotlib not installed for plotting, calculation test succeeded.")',
    ])

    return "\n".join(lines)


def generate_desmos_syntax(epicycles: List[Epicycle], precision: int = 4, max_terms: int = 25) -> str:
    """
    Generates Desmos-ready parametric syntax: (X(t), Y(t)) with 0 <= t <= 1.
    """
    shown = epicycles[:max_terms]
    x_parts = []
    y_parts = []

    for ep in shown:
        if ep.radius < 1e-5:
            continue
        r = format_number(ep.radius, precision)
        freq = ep.freq
        phi = ep.phase

        if freq == 0:
            cx = format_number(ep.coeff.real, precision)
            cy = format_number(ep.coeff.imag, precision)
            x_parts.append(cx)
            y_parts.append(cy)
            continue

        phi_str = f" + {format_number(phi, precision)}" if abs(phi) > 1e-4 else ""
        if phi < 0:
            phi_str = f" - {format_number(abs(phi), precision)}"

        arg = f"2\\pi \\cdot {freq} t{phi_str}"
        x_parts.append(f"{r}\\cos({arg})")
        y_parts.append(f"{r}\\sin({arg})")

    x_str = " + ".join(x_parts) if x_parts else "0"
    y_str = " + ".join(y_parts) if y_parts else "0"

    desmos = f"({x_str}, {y_str})\n\\text{{wobei }} 0 \\le t \\le 1"
    return desmos


def generate_javascript_code(epicycles: List[Epicycle], precision: int = 6) -> str:
    """
    Generates runnable JavaScript function.
    """
    lines = [
        "// Fourier Epicycles Curve Function",
        "const EPICYCLES = [",
    ]
    for ep in epicycles:
        lines.append(f"  {{ freq: {ep.freq}, radius: {ep.radius:.{precision}f}, phase: {ep.phase:.{precision}f} }},")
    lines.extend([
        "];",
        "",
        "function evaluateCurve(t) {",
        "  let x = 0.0;",
        "  let y = 0.0;",
        "  const twoPi = 2.0 * Math.PI;",
        "  for (const ep of EPICYCLES) {",
        "    const angle = twoPi * ep.freq * t + ep.phase;",
        "    x += ep.radius * Math.cos(angle);",
        "    y += ep.radius * Math.sin(angle);",
        "  }",
        "  return { x, y };",
        "}",
    ])
    return "\n".join(lines)
