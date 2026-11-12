"""
Preset Curves and Geometric Shapes for quick demonstration and testing.
Provides initial control points on the XY plane for various interesting curves.
"""

import math
from typing import List, Tuple, Dict
import numpy as np


def get_circle_points(radius: float = 150.0, num_points: int = 8, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    for i in range(num_points):
        angle = 2.0 * math.pi * i / num_points
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        pts.append((round(x, 2), round(y, 2)))
    return pts


def get_heart_points(scale: float = 12.0, num_points: int = 16, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    ts = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
    for t in ts:
        # Classical heart curve: x = 16 sin^3(t), y = 13 cos(t) - 5 cos(2t) - 2 cos(3t) - cos(4t)
        x = scale * 16 * (math.sin(t) ** 3)
        y = scale * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
        pts.append((round(center[0] + x, 2), round(center[1] + y, 2)))
    return pts


def get_infinity_points(width: float = 220.0, height: float = 110.0, num_points: int = 16, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    ts = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
    for t in ts:
        # Lemniscate of Gerono / Bernoulli
        denom = 1 + math.sin(t)**2
        x = width * math.cos(t) / denom
        y = height * math.sin(t) * math.cos(t) / denom
        pts.append((round(center[0] + x, 2), round(center[1] + y, 2)))
    return pts


def get_star_points(outer_r: float = 160.0, inner_r: float = 70.0, points_count: int = 5, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    total = points_count * 2
    for i in range(total):
        r = outer_r if (i % 2 == 0) else inner_r
        angle = math.pi / 2.0 + 2.0 * math.pi * i / total
        x = center[0] + r * math.cos(angle)
        y = center[1] + r * math.sin(angle)
        pts.append((round(x, 2), round(y, 2)))
    return pts


def get_trefoil_points(scale: float = 55.0, num_points: int = 24, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    ts = np.linspace(0, 2 * math.pi, num_points, endpoint=False)
    for t in ts:
        x = scale * (math.sin(t) + 2 * math.sin(2 * t))
        y = scale * (math.cos(t) - 2 * math.cos(2 * t))
        pts.append((round(center[0] + x, 2), round(center[1] + y, 2)))
    return pts


def get_wave_points(width: float = 400.0, amplitude: float = 120.0, num_points: int = 9, center: Tuple[float, float] = (0, 0)) -> List[Tuple[float, float]]:
    pts = []
    xs = np.linspace(-width / 2.0, width / 2.0, num_points)
    for x in xs:
        t = (x + width / 2.0) / width * 2 * math.pi
        y = amplitude * math.sin(t)
        pts.append((round(center[0] + x, 2), round(center[1] + y, 2)))
    return pts


PRESETS: Dict[str, callable] = {
    "Herz (Heart)": get_heart_points,
    "Unendlichkeit (Lemniskate)": get_infinity_points,
    "5-Zack Stern (Star)": get_star_points,
    "Kleeblatt / Trefoil": get_trefoil_points,
    "Kreis (Circle)": get_circle_points,
    "S-Welle (Wave - Offen)": get_wave_points,
}
