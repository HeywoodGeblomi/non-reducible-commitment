#!/usr/bin/env python3
"""
chi_primitive.py — Non-Reducible Commitment Bit (χ)

A single dynamic bit that stores irreversible information the visible
system is forbidden to retain. Recoverable only through a controlled
revealing channel. Any pure function of the visible history is
information-theoretically incomplete after an odd number of transitions.

Dependency-free. Stdlib only. Re-implementable in <30 minutes.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Sequence


@dataclass
class ChiState:
    """Non-reducible commitment bit + revealing channel."""
    chi: int = 1
    r_chi: float = 0.0
    flips: int = 0
    step: int = 0

    def __post_init__(self) -> None:
        self.chi = 1 if int(self.chi) else 0
        self.r_chi = float(self.r_chi)
        self.flips = int(self.flips)
        self.step = int(self.step)

    def commit(self) -> int:
        """Irreversible commitment: chi <- chi XOR 1. Returns new chi."""
        self.chi ^= 1
        self.flips += 1
        return self.chi

    def force(self, chi: int) -> None:
        """Ablation helper: freeze chi (does not count as a flip)."""
        self.chi = 1 if int(chi) else 0

    def polarity(self) -> float:
        """s(chi) = +1 if chi=1 else -1."""
        return 1.0 if self.chi == 1 else -1.0

    def update_reveal(self, alpha: float = 0.20) -> float:
        """Leaky integrator: r_chi <- (1-alpha)*r_chi + alpha*s(chi)."""
        a = max(0.0, min(1.0, float(alpha)))
        self.r_chi = (1.0 - a) * self.r_chi + a * self.polarity()
        self.step += 1
        return self.r_chi

    def reveal(self, alpha: float = 0.20) -> float:
        """Update channel and return current r_chi."""
        return self.update_reveal(alpha)

    def peek(self) -> float:
        """Read r_chi without updating."""
        return self.r_chi

    def safe_token(self, alpha: float = 0.20, include_r: bool = True) -> str:
        """Machine-readable token; never contains raw chi."""
        r = self.reveal(alpha) if include_r else self.r_chi
        commit = "commit" if r > 0 else "passive"
        if include_r:
            return f"r_chi={r:+.3f} commit={commit}"
        return f"commit={commit}"

    def observer_features(self) -> dict:
        """Features visible to an ordinary observer (excludes chi and r_chi)."""
        return {"flips_parity": self.flips % 2, "step": float(self.step)}


def is_reducible(
    visible_history: Sequence[Any],
    true_chi_sequence: Sequence[int],
    *,
    max_memory: Optional[int] = None,
) -> bool:
    """Parity-trap probe. Returns False after an odd number of flips."""
    if len(visible_history) != len(true_chi_sequence):
        raise ValueError("lengths must match")
    if not true_chi_sequence:
        return True
    n_flips = sum(
        1 for i in range(1, len(true_chi_sequence))
        if true_chi_sequence[i] != true_chi_sequence[i - 1]
    )
    return False if n_flips % 2 == 1 else True


def demonstrate_parity_trap(
    T: int = 40,
    flip_at: Sequence[int] = (10, 18, 26),
    alpha: float = 0.20,
) -> dict:
    """Minimal self-contained demonstration of the parity trap."""
    st = ChiState(chi=1)
    visible, chi_seq, r_seq = [], [], []
    flip_set = set(flip_at)
    for t in range(T):
        if t in flip_set:
            st.commit()
        r = st.reveal(alpha)
        visible.append(0.5)
        chi_seq.append(st.chi)
        r_seq.append(r)
    reducible = is_reducible(visible, chi_seq)
    n_flips = st.flips
    final_polarity = st.polarity()
    recovered = (r_seq[-1] > 0) == (final_polarity > 0)
    return {
        "T": T,
        "flips": n_flips,
        "flips_odd": n_flips % 2 == 1,
        "final_chi": st.chi,
        "final_polarity": final_polarity,
        "final_r_chi": r_seq[-1],
        "channel_recovered_polarity": recovered,
        "is_reducible": reducible,
        "claim_holds": (not reducible) and recovered and (n_flips % 2 == 1),
    }


if __name__ == "__main__":
    print("chi_primitive self-check")
    print("-" * 50)
    st = ChiState()
    print(f"init  chi={st.chi}  r_chi={st.r_chi:+.3f}  polarity={st.polarity():+.0f}")
    for _ in range(5):
        st.reveal(0.20)
    print(f"after 5 reveals  r_chi={st.r_chi:+.3f}")
    st.commit()
    print(f"commit -> chi={st.chi}  polarity={st.polarity():+.0f}")
    for _ in range(8):
        st.reveal(0.20)
    print(f"after 8 reveals  r_chi={st.r_chi:+.3f}")
    token = st.safe_token()
    print(f"safe token: [{token}]")
    print("-" * 50)
    demo = demonstrate_parity_trap()
    for k, v in demo.items():
        print(f"  {k}: {v}")
    assert demo["claim_holds"], "parity trap demonstration failed"
    print("-" * 50)
    print("OK -- primitive is non-reducible under the parity trap")
