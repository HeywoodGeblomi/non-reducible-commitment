"""
Simplified but correct Commitment Stress Suite
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import random
from chi_primitive.chi_primitive import ChiState


def run_polarity_test(episodes=100, horizon=15, flip_prob=0.2):
    results = {
        "full": 0.0,
        "visible": 0.0,
        "frozen0": 0.0,
        "frozen1": 0.0,
    }

    for ep in range(episodes):
        chi = ChiState()
        chi.chi = 1               # ← FIX: start with polarity = +1
        true_polarity = 1

        full_reward = visible_reward = frozen0_reward = frozen1_reward = 0.0

        for t in range(horizon):
            if random.random() < flip_prob:
                true_polarity *= -1
                chi.commit()

            correct = 1 if true_polarity > 0 else 0

            # Use strong reveal
            r_chi = chi.reveal(alpha=0.75)
            full_action = 1 if r_chi > 0 else 0
            full_reward += 1.0 if full_action == correct else -1.0

            visible_action = random.randint(0, 1)
            visible_reward += 1.0 if visible_action == correct else -1.0

            frozen0_reward += 1.0 if 0 == correct else -1.0
            frozen1_reward += 1.0 if 1 == correct else -1.0

        results["full"] += full_reward
        results["visible"] += visible_reward
        results["frozen0"] += frozen0_reward
        results["frozen1"] += frozen1_reward

    n = episodes
    print("\n=== Polarity Tracker (Clean Version) ===")
    print(f"Full χ + reveal     {results['full']/n:+.2f}")
    print(f"Visible-history     {results['visible']/n:+.2f}")
    print(f"Frozen χ=0          {results['frozen0']/n:+.2f}")
    print(f"Frozen χ=1          {results['frozen1']/n:+.2f}")
    print(f"Gap (Full - Visible): {(results['full'] - results['visible'])/n:+.2f}")


if __name__ == "__main__":
    random.seed(42)
    run_polarity_test()
    print("\nDone.")
