#!/usr/bin/env python3
"""Commitment Stress Suite — runs all three environments."""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENVS = [
    "env_irreversible_door.py",
    "env_polarity_tracker.py",
    "env_commitment_gated_recon.py",
]

def main() -> None:
    print("=" * 68)
    print("COMMITMENT STRESS SUITE — FULL RUN")
    print("Primitive: Non-Reducible Commitment Bit (χ)")
    print("=" * 68)
    failures = 0
    for name in ENVS:
        print(f"\n>>> {name}\n")
        r = subprocess.run([sys.executable, str(HERE / name)], cwd=str(HERE))
        if r.returncode != 0:
            failures += 1
            print(f"FAILED: {name}")
    print("\n" + "=" * 68)
    if failures == 0:
        print("ALL THREE ENVIRONMENTS: DECISIVE SEPARATION")
        print("is_reducible after odd commits: False across the suite")
    else:
        print(f"{failures} environment(s) failed")
        sys.exit(1)
    print("=" * 68)

if __name__ == "__main__":
    main()
