"""
Spline Generation and Evaluation Module.
Supports Catmull-Rom, Cubic Spline Interpolation, Cubic Bézier, and B-Splines.
Includes arc-length uniform resampling for smooth Fourier analysis.
"""

import math
from typing import List, Tuple, Sequence
import numpy as np


def resample_polyline(points: np.ndarray, num_samples: int = 500, closed: bool = False) -> np.ndarray:
    """
    Resample a polyline uniformly along arc length.
    points: shape (N, 2)
    """
    if len(points) < 2:
        return np.array(points, dtype=float)

    pts = list(points)
    if closed and (pts[0] != pts[-1]).any():
        pts.append(pts[0])
    pts = np.array(pts, dtype=float)

    # Compute segment distances
    diffs = np.diff(pts, axis=0)
    dists = np.sqrt((diffs ** 2).sum(axis=1))
    cumulative = np.zeros(len(pts))
    cumulative[1:] = np.cumsum(dists)
    total_len = cumulative[-1]

    if total_len == 0:
        return np.tile(pts[0], (num_samples, 1))

    # Sample uniformly along arc length
    sample_dists = np.linspace(0, total_len, num_samples, endpoint=not closed)
    resampled_x = np.interp(sample_dists, cumulative, pts[:, 0])
    resampled_y = np.interp(sample_dists, cumulative, pts[:, 1])

    return np.column_stack((resampled_x, resampled_y))


def catmull_rom_spline(
    control_points: Sequence[Sequence[float]],
    num_samples: int = 600,
    closed: bool = False,
    alpha: float = 0.5  # 0: uniform, 0.5: centripetal, 1: chordal
) -> np.ndarray:
    """
    Catmull-Rom spline interpolation through control points.
    Passes directly through all control points with smooth C1 continuity.
    """
    pts = [np.array(p, dtype=float) for p in control_points]
    if len(pts) < 2:
        return np.array(pts, dtype=float)
    if len(pts) == 2:
        return resample_polyline(np.array(pts), num_samples=num_samples, closed=closed)

    if closed:
        # Wrap around
        extended = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        # Extrapolate ghost endpoints
        p_start = 2 * pts[0] - pts[1]
        p_end = 2 * pts[-1] - pts[-2]
        extended = [p_start] + pts + [p_end]

    def get_t(t: float, p0: np.ndarray, p1: np.ndarray) -> float:
        dist = np.linalg.norm(p1 - p0)
        return t + (dist ** alpha if dist > 0 else 1.0)

    curve_points = []
    num_segments = len(extended) - 3
    samples_per_seg = max(4, num_samples // num_segments)

    for i in range(num_segments):
        p0, p1, p2, p3 = extended[i], extended[i + 1], extended[i + 2], extended[i + 3]
        t0 = 0.0
        t1 = get_t(t0, p0, p1)
        t2 = get_t(t1, p1, p2)
        t3 = get_t(t2, p2, p3)

        if abs(t2 - t1) < 1e-9:
            continue

        ts = np.linspace(t1, t2, samples_per_seg, endpoint=(i == num_segments - 1))
        for t in ts:
            # Barry and Goldman pyramid algorithm
            a1 = (t1 - t) / (t1 - t0) * p0 + (t - t0) / (t1 - t0) * p1 if abs(t1 - t0) > 1e-9 else p1
            a2 = (t2 - t) / (t2 - t1) * p1 + (t - t1) / (t2 - t1) * p2
            a3 = (t3 - t) / (t3 - t2) * p2 + (t - t2) / (t3 - t2) * p3 if abs(t3 - t2) > 1e-9 else p2

            b1 = (t2 - t) / (t2 - t0) * a1 + (t - t0) / (t2 - t0) * a2 if abs(t2 - t0) > 1e-9 else a2
            b2 = (t3 - t) / (t3 - t1) * a2 + (t - t1) / (t3 - t1) * a3 if abs(t3 - t1) > 1e-9 else a2

            c = (t2 - t) / (t2 - t1) * b1 + (t - t1) / (t2 - t1) * b2
            curve_points.append(c)

    res = np.array(curve_points) if curve_points else np.array(pts)
    return resample_polyline(res, num_samples=num_samples, closed=closed)


def natural_cubic_spline(
    control_points: Sequence[Sequence[float]],
    num_samples: int = 600,
    closed: bool = False
) -> np.ndarray:
    """
    Natural or periodic cubic spline passing through all control points with C2 continuity.
    """
    pts = np.array(control_points, dtype=float)
    n = len(pts)
    if n < 2:
        return pts
    if n == 2:
        return resample_polyline(pts, num_samples, closed)

    if closed:
        # Append first point to close loop
        pts = np.vstack([pts, pts[0]])
        n = len(pts)

    # Chord length parameterization
    diffs = np.diff(pts, axis=0)
    dists = np.sqrt((diffs ** 2).sum(axis=1))
    t = np.zeros(n)
    t[1:] = np.cumsum(dists)
    if t[-1] == 0:
        return np.tile(pts[0], (num_samples, 1))
    t /= t[-1]  # normalize to [0, 1]

    # For each coordinate x and y, fit natural cubic spline
    def fit_1d(values: np.ndarray, knots: np.ndarray):
        m = len(knots) - 1
        h = np.diff(knots)
        h = np.maximum(h, 1e-9)

        # Tridiagonal system for second derivatives M
        alpha = np.zeros(m)
        for i in range(1, m):
            alpha[i] = (3.0 / h[i]) * (values[i + 1] - values[i]) - (3.0 / h[i - 1]) * (values[i] - values[i - 1])

        l = np.ones(m + 1)
        mu = np.zeros(m + 1)
        z = np.zeros(m + 1)

        l[0] = 1.0
        mu[0] = 0.0
        z[0] = 0.0

        for i in range(1, m):
            l[i] = 2.0 * (knots[i + 1] - knots[i - 1]) - h[i - 1] * mu[i - 1]
            if abs(l[i]) < 1e-9:
                l[i] = 1e-9
            mu[i] = h[i] / l[i]
            z[i] = (alpha[i] - h[i - 1] * z[i - 1]) / l[i]

        l[m] = 1.0
        z[m] = 0.0
        c = np.zeros(m + 1)
        b = np.zeros(m)
        d = np.zeros(m)

        for j in range(m - 1, -1, -1):
            c[j] = z[j] - mu[j] * c[j + 1]
            b[j] = (values[j + 1] - values[j]) / h[j] - h[j] * (c[j + 1] + 2.0 * c[j]) / 3.0
            d[j] = (c[j + 1] - c[j]) / (3.0 * h[j])

        # Evaluation function
        def eval_spline(u: np.ndarray) -> np.ndarray:
            res = np.zeros_like(u)
            idx = np.searchsorted(knots, u) - 1
            idx = np.clip(idx, 0, m - 1)
            dx = u - knots[idx]
            return values[idx] + b[idx] * dx + c[idx] * (dx ** 2) + d[idx] * (dx ** 3)

        return eval_spline

    eval_x = fit_1d(pts[:, 0], t)
    eval_y = fit_1d(pts[:, 1], t)

    u_samples = np.linspace(0.0, 1.0, num_samples, endpoint=not closed)
    res_x = eval_x(u_samples)
    res_y = eval_y(u_samples)

    result = np.column_stack((res_x, res_y))
    return resample_polyline(result, num_samples, closed)


def uniform_b_spline(
    control_points: Sequence[Sequence[float]],
    num_samples: int = 600,
    closed: bool = False
) -> np.ndarray:
    """
    Uniform Cubic B-Spline curve.
    Extremely smooth C2 curve approximating the control polygon.
    """
    pts = [np.array(p, dtype=float) for p in control_points]
    if len(pts) < 4:
        return catmull_rom_spline(pts, num_samples, closed)

    if closed:
        extended = pts + pts[:3]
    else:
        # Repeat endpoints 3 times for clamped B-spline
        extended = [pts[0], pts[0]] + pts + [pts[-1], pts[-1]]

    num_segments = len(extended) - 3
    samples_per_seg = max(4, num_samples // num_segments)
    curve_points = []

    # Basis matrix for cubic B-spline
    M = (1.0 / 6.0) * np.array([
        [-1,  3, -3,  1],
        [ 3, -6,  3,  0],
        [-3,  0,  3,  0],
        [ 1,  4,  1,  0]
    ])

    for i in range(num_segments):
        p_block = np.array([extended[i], extended[i + 1], extended[i + 2], extended[i + 3]])
        ts = np.linspace(0, 1, samples_per_seg, endpoint=(i == num_segments - 1))
        t_mat = np.column_stack([ts**3, ts**2, ts, np.ones_like(ts)])
        seg_points = t_mat @ (M @ p_block)
        curve_points.append(seg_points)

    result = np.vstack(curve_points)
    return resample_polyline(result, num_samples, closed)


def bezier_spline(
    control_points: Sequence[Sequence[float]],
    num_samples: int = 600,
    closed: bool = False
) -> np.ndarray:
    """
    Composite Bézier curve.
    If arbitrary points are given, automatically constructs smooth G1 tangent handles.
    """
    pts = [np.array(p, dtype=float) for p in control_points]
    n = len(pts)
    if n < 2:
        return np.array(pts, dtype=float)
    if n == 2:
        return resample_polyline(np.array(pts), num_samples, closed)

    # If already a set of bezier segments or just control points:
    # We generate smooth handles using 1/3 distance to neighboring points
    handles_left = [None] * n
    handles_right = [None] * n

    for i in range(n):
        if closed:
            prev_p = pts[(i - 1) % n]
            next_p = pts[(i + 1) % n]
        else:
            prev_p = pts[max(0, i - 1)]
            next_p = pts[min(n - 1, i + 1)]

        tangent = (next_p - prev_p) / 6.0
        handles_right[i] = pts[i] + tangent
        handles_left[i] = pts[i] - tangent

    num_segments = n if closed else n - 1
    samples_per_seg = max(4, num_samples // num_segments)
    curve_points = []

    for i in range(num_segments):
        i_next = (i + 1) % n
        p0 = pts[i]
        p1 = handles_right[i]
        p2 = handles_left[i_next]
        p3 = pts[i_next]

        ts = np.linspace(0, 1, samples_per_seg, endpoint=(i == num_segments - 1))
        # Cubic Bézier formula: (1-t)^3 p0 + 3(1-t)^2 t p1 + 3(1-t) t^2 p2 + t^3 p3
        t_mat = np.column_stack([
            (1 - ts)**3,
            3 * (1 - ts)**2 * ts,
            3 * (1 - ts) * ts**2,
            ts**3
        ])
        seg = t_mat @ np.array([p0, p1, p2, p3])
        curve_points.append(seg)

    result = np.vstack(curve_points)
    return resample_polyline(result, num_samples, closed)


def linear_spline(
    control_points: Sequence[Sequence[float]],
    num_samples: int = 600,
    closed: bool = False
) -> np.ndarray:
    """
    Linear polyline connecting control points.
    """
    pts = np.array(control_points, dtype=float)
    return resample_polyline(pts, num_samples, closed)


SPLINE_ALGORITHMS = {
    "Catmull-Rom (Interpolierend)": catmull_rom_spline,
    "Kubischer Spline (C2 Natural)": natural_cubic_spline,
    "Bézier Spline (G1 Glatt)": bezier_spline,
    "B-Spline (Approximierend)": uniform_b_spline,
    "Polygonzug (Linear)": linear_spline,
}
