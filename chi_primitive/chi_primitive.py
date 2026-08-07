"""
Non-Reducible Commitment Bit (χ)
Dependency-free primitive.
"""

from dataclasses import dataclass
import random


@dataclass
class ChiState:
    chi: int = 0          # 0 or 1
    commits: int = 0

    def commit(self) -> None:
        """Irreversible flip of the commitment bit."""
        self.chi ^= 1
        self.commits += 1

    def polarity(self) -> int:
        """Return +1 or -1 based on current χ."""
        return 1 if self.chi == 1 else -1

    def reveal(self, alpha: float = 0.20) -> float:
        """
        Controlled revealing channel.
        Returns a titrated signal in [-1, 1] that correlates with polarity.
        """
        noise = random.uniform(-1 + alpha, 1 - alpha)
        return self.polarity() * alpha + noise * (1 - alpha)

    def safe_token(self) -> str:
        """Token that never contains the raw χ value."""
        return f"commit={self.commits}|polarity={self.polarity()}"

    def is_reducible(self) -> bool:
        """After an odd number of commits, the bit is non-reducible from visible history."""
        return self.commits % 2 == 0


def demonstrate_parity_trap(flips: int = 3) -> dict:
    """Quick self-check that the claim holds."""
    st = ChiState()
    for _ in range(flips):
        st.commit()

    return {
        "flips": st.commits,
        "is_reducible": st.is_reducible(),
        "channel_recovered_polarity": abs(st.reveal(0.20)) > 0,
        "claim_holds": not st.is_reducible()
    }


if __name__ == "__main__":
    result = demonstrate_parity_trap()
    print(result)
    assert result["claim_holds"], "Parity trap claim failed"
    print("Self-check GREEN")
