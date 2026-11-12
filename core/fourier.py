"""
Discrete Fourier Transform and Epicycles Decomposition Module.
Transforms any 2D spline curve into rotating complex vectors (epicycles).
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
import numpy as np


@dataclass
class Epicycle:
    freq: int           # Frequency k (can be negative, 0, or positive)
    radius: float       # Amplitude |c_k|
    phase: float        # Initial phase in radians arg(c_k)
    coeff: complex      # Raw Fourier coefficient c_k
    energy: float       # Relative power/amplitude contribution


class FourierSeries2D:
    def __init__(self, curve_points: np.ndarray, max_harmonics: Optional[int] = None):
        """
        curve_points: np.ndarray of shape (N, 2), ordered along the curve.
        """
        self.raw_points = np.array(curve_points, dtype=float)
        self.num_samples = len(self.raw_points)
        self.epicycles: List[Epicycle] = []
        self.sorted_epicycles: List[Epicycle] = []
        self.dc_offset = 0.0 + 0.0j

        if self.num_samples >= 2:
            self._compute_dft(max_harmonics)

    def _compute_dft(self, max_harmonics: Optional[int] = None):
        N = self.num_samples
        # Convert 2D points (x, y) into complex numbers z = x + i*y
        z = self.raw_points[:, 0] + 1j * self.raw_points[:, 1]

        # Use FFT for lightning fast and exact DFT
        fft_vals = np.fft.fft(z) / N
        fft_freqs = np.fft.fftfreq(N, d=1.0 / N)  # frequencies in integer cycles

        epicycles_list = []
        total_energy = 0.0

        for coeff, freq in zip(fft_vals, fft_freqs):
            k = int(round(freq))
            radius = float(np.abs(coeff))
            phase = float(np.angle(coeff))
            total_energy += radius ** 2
            epicycles_list.append(Epicycle(
                freq=k,
                radius=radius,
                phase=phase,
                coeff=complex(coeff),
                energy=radius ** 2
            ))

        if total_energy > 0:
            for ep in epicycles_list:
                ep.energy = (ep.energy / total_energy) * 100.0

        self.epicycles = epicycles_list

        # Extract DC offset (k = 0)
        dc_list = [ep for ep in epicycles_list if ep.freq == 0]
        if dc_list:
            self.dc_offset = dc_list[0].coeff
            other_eps = [ep for ep in epicycles_list if ep.freq != 0]
        else:
            self.dc_offset = 0.0 + 0.0j
            other_eps = epicycles_list

        # Sort remaining epicycles by radius descending (largest circles first)
        other_eps.sort(key=lambda ep: ep.radius, reverse=True)

        if max_harmonics is not None and max_harmonics > 0:
            other_eps = other_eps[:max_harmonics]

        # In standard epicycles visualization, first element is DC offset (freq 0),
        # followed by sorted harmonics
        if dc_list:
            self.sorted_epicycles = [dc_list[0]] + other_eps
        else:
            self.sorted_epicycles = other_eps

    def get_active_epicycles(self, count: int) -> List[Epicycle]:
        """Return the top `count` epicycles (including DC offset)."""
        if not self.sorted_epicycles:
            return []
        count = max(1, min(count, len(self.sorted_epicycles)))
        return self.sorted_epicycles[:count]

    def evaluate_chain(self, t: float, num_epicycles: int) -> Tuple[List[Tuple[float, float]], List[float], Tuple[float, float]]:
        """
        Evaluate the epicycle chain at normalized time t in [0, 1].
        Returns:
            centers: list of (x, y) coordinates for the centers of each epicycle circle
            radii: list of radius values for each circle
            tip: final (x, y) tip coordinate where the pen is
        """
        active = self.get_active_epicycles(num_epicycles)
        if not active:
            return [], [], (0.0, 0.0)

        centers = []
        radii = []

        current_z = 0.0 + 0.0j
        two_pi = 2.0 * math.pi

        for i, ep in enumerate(active):
            # Center of this circle
            cx, cy = current_z.real, current_z.imag
            centers.append((cx, cy))
            radii.append(ep.radius)

            # Advance to tip of this vector
            angle = two_pi * ep.freq * t + ep.phase
            vector = ep.radius * (math.cos(angle) + 1j * math.sin(angle))
            current_z += vector

        tip = (current_z.real, current_z.imag)
        return centers, radii, tip

    def evaluate_reconstruction(self, num_epicycles: int, num_points: int = 500) -> np.ndarray:
        """
        Generate the full reconstructed curve for t in [0, 1] using `num_epicycles`.
        Returns shape (num_points, 2).
        """
        active = self.get_active_epicycles(num_epicycles)
        if not active:
            return np.zeros((0, 2))

        ts = np.linspace(0.0, 1.0, num_points, endpoint=True)
        two_pi = 2.0 * math.pi

        z_sum = np.zeros(num_points, dtype=complex)
        for ep in active:
            angles = two_pi * ep.freq * ts + ep.phase
            z_sum += ep.radius * (np.cos(angles) + 1j * np.sin(angles))

        return np.column_stack((z_sum.real, z_sum.imag))

    def compute_approximation_error(self, num_epicycles: int) -> Tuple[float, float]:
        """
        Compute mean and max Euclidean distance error between original curve and Fourier reconstruction.
        """
        recon = self.evaluate_reconstruction(num_epicycles, num_points=self.num_samples)
        if len(recon) != len(self.raw_points) or len(recon) == 0:
            return 0.0, 0.0
        dists = np.linalg.norm(self.raw_points - recon, axis=1)
        return float(np.mean(dists)), float(np.max(dists))
