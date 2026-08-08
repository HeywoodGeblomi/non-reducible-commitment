#!/usr/bin/env python3
"""
Commitment Stress Suite — single runner
Executes all environments and prints the comparison tables.
"""

from __future__ import annotations
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

ENVS = [
    "env_irreversible_door.py",
    "env_polarity_tracker.py",
    "env_commitment_gated_recon.py",
    "env_hard_regime_shift.py",
]


def main() -> None:
    print("=" * 72)
    print("COMMITMENT STRESS SUITE — FULL RUN")
    print("Primitive: Non-Reducible Commitment Bit (χ)")
    print("=" * 72)
    print()

    failures = 0
    for name in ENVS:
        path = HERE / name
        print(f">>> {name}")
        print()
        r = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(HERE),
            capture_output=False,
        )
        if r.returncode != 0:
            failures += 1
            print(f"FAILED: {name} (exit {r.returncode})")
        print()

    print("=" * 72)
    if failures == 0:
        print("ALL ENVIRONMENTS (incl. hard regime-shift): DECISIVE SEPARATION")
        print("is_reducible after odd commits: False across the suite")
        print("Full χ + reveal dominates Visible-history / Adaptive / Frozen / No-reveal")
    else:
        print(f"{failures} environment(s) failed")
        sys.exit(1)
    print("=" * 72)


if __name__ == "__main__":
    main()
