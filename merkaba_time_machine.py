#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merkaba Time Machine — counter-rotating tetrahedra as temporal generator
Author: Ziyavutdinov Magomed Kamalovich (Zimaka)
License: MIT
"""
import math
import argparse

__author__ = "Зиявутдинов Магомед Камалович (Zimaka)"
__version__ = "1.0.0"
__license__ = "MIT"

PHI = (1.0 + math.sqrt(5.0)) / 2.0
INV_PHI = PHI - 1.0
TWO_PI = 2.0 * math.pi
C_ABSOLUTE = 10.0
GAMMA_MAX = 1e5
EPS = 0.25
COOLDOWN = 3


def lorentz_gamma(v_fraction):
    """γ = 1/√(1 − β²)."""
    if v_fraction >= 1.0:
        return GAMMA_MAX
    b2 = v_fraction * v_fraction
    return min(1.0 / math.sqrt(max(1.0 - b2, 1e-15)), GAMMA_MAX)


class Merkaba:
    """
    Two counter-rotating tetrahedra.
    Upper: v = v_upper · C_ABSOLUTE (forward in time).
    Lower: v = v_lower · C_ABSOLUTE (backward in time).
    Cell born when |Δangle − π| < EPS.
    """

    UPPER_COUNT = 3
    LOWER_COUNT = 3

    def __init__(self, mode="asymmetric", dt=0.02):
        self.mode = mode
        self.dt = dt
        self.step_count = 0
        self.cells_born = 0

        if mode == "symmetric":
            self.v_upper = 9/9
            self.v_lower = 9/9
        elif mode == "light":
            self.v_upper = 9/9
            self.v_lower = 8/9
        else:  # asymmetric
            self.v_upper = PHI
            self.v_lower = INV_PHI

        self.omega_upper = +self.v_upper * (C_ABSOLUTE / 100.0)
        self.omega_lower = -self.v_lower * (C_ABSOLUTE / 100.0)
        self.gamma_upper = lorentz_gamma(self.v_upper)
        self.gamma_lower = lorentz_gamma(self.v_lower)

        self.upper = [{"angle": i * TWO_PI / self.UPPER_COUNT}
                      for i in range(self.UPPER_COUNT)]
        self.lower = [{"angle": i * TWO_PI / self.LOWER_COUNT + math.pi/3}
                      for i in range(self.LOWER_COUNT)]
        self.cooldown = {(i, j): 0
                         for i in range(self.UPPER_COUNT)
                         for j in range(self.LOWER_COUNT)}
        self.center_coherence = 0.5

    def step(self):
        for v in self.upper:
            v["angle"] = (v["angle"] + self.omega_upper * self.dt) % TWO_PI
        for v in self.lower:
            v["angle"] = (v["angle"] + self.omega_lower * self.dt) % TWO_PI

        new_cells = []
        for i, up in enumerate(self.upper):
            for j, lo in enumerate(self.lower):
                if self.cooldown[(i, j)] > 0:
                    self.cooldown[(i, j)] -= 1
                    continue
                d = (up["angle"] - lo["angle"] + math.pi) % TWO_PI - math.pi
                if abs(abs(d) - math.pi) < EPS:
                    phase = (up["angle"] + lo["angle"]) / 2.0
                    new_cells.append({
                        "phase": phase,
                        "energy": self.v_upper * self.v_lower,
                        "source": (i, j),
                        "gamma_birth": self.gamma_lower,
                    })
                    self.cooldown[(i, j)] = COOLDOWN
                    self.cells_born += 1

        up_m = sum(v["angle"] for v in self.upper) / self.UPPER_COUNT
        lo_m = sum(v["angle"] for v in self.lower) / self.LOWER_COUNT
        self.center_coherence = (math.cos(up_m - lo_m) + 1) / 2.0
        self.step_count += 1
        return new_cells

    def report(self):
        return (
            f"Merkaba Time Machine (mode={self.mode})\n"
            f"  Upper: v = {self.v_upper:.4f}c → γ = {self.gamma_upper:.2f} "
            f"({'outside time' if self.gamma_upper >= GAMMA_MAX else 'slow'})\n"
            f"  Lower: v = {self.v_lower:.4f}c → γ = {self.gamma_lower:.4f} "
            f"(in time)\n"
            f"  Coherence: {self.center_coherence:.4f}\n"
            f"  Cells born: {self.cells_born}\n"
            f"  Steps: {self.step_count}"
        )


def selftest():
    print("=" * 60)
    print(f"MERKABA TIME MACHINE v{__version__} — SELFTEST")
    print("=" * 60)

    for mode in ["symmetric", "asymmetric", "light"]:
        print(f"\n--- mode: {mode} ---")
        m = Merkaba(mode=mode, dt=0.05)
        cells_total = 0
        for _ in range(50):
            cells = m.step()
            cells_total += len(cells)
        print(m.report())
        print(f"  Total cells in 50 steps: {cells_total}")

    print("\n✅ SELFTEST passed")
    print(f"Author: {__author__}")


def main():
    parser = argparse.ArgumentParser(
        description=f"Merkaba Time Machine v{__version__}")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--mode", default="asymmetric",
                        choices=["symmetric", "asymmetric", "light"])
    parser.add_argument("--steps", type=int, default=50)
    args = parser.parse_args()
    selftest()


if __name__ == "__main__":
    main()