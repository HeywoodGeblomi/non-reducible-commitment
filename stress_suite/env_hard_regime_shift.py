#!/usr/bin/env python3
"""
Hard Regime-Shift variant — longer horizon + non-stationary but
observationally-equivalent observation regimes.

Goal: stress the parity-trap claim under conditions closer to
continual / open-world settings while remaining fully synthetic
and runnable in the current environment.

Construction
------------
- Horizon 80.
- Hidden polarity flips at random intervals (same as Polarity Tracker).
- Observation distribution undergoes discrete regime shifts
  (mean / support change), but the *same* shift is applied under
  both polarities → pure functions of the visible residual still
  cannot recover polarity after an odd number of flips.
- Sparse / delayed reward structure: reward is given every step
  but the optimal action is determined solely by current polarity.
- Adaptive pure-visible baselines from the strengthened suite are
  re-used and must still collapse.

Full χ + reveal must retain near-ceiling performance.

This is a controlled stress test of the engineered process class
P_parity. It does not claim necessity on real agent trajectories.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chi_primitive import ChiState


class HardRegimeShift:
    """
    Horizon H ≈ 80.
    Hidden polarity flips with probability flip_prob.
    Observation regime changes every regime_len steps (same change
    under both polarities).
    Reward = +1 if action matches current polarity else −1.
    """

    def __init__(
        self,
        horizon: int = 80,
        flip_prob: float = 0.12,
        regime_len: int = 16,
        seed: int = 42,
    ):
        self.horizon = int(horizon)
        self.flip_prob = float(flip_prob)
        self.regime_len = int(regime_len)
        self.rng = random.Random(seed)
        self.reset(seed=seed)

    def _regime_params(self, regime_id: int) -> Tuple[int, int]:
        supports = [(0, 1), (1, 3), (0, 2), (2, 4), (0, 3)]
        return supports[regime_id % len(supports)]

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            self.rng = random.Random(seed)
        self.t = 0
        self.chi = ChiState(chi=1)
        self.true_polarity = 1.0
        self.done = False
        self.total_reward = 0.0
        self.flip_count = 0
        self.regime_id = 0
        for _ in range(6):
            self.chi.reveal(0.40)
        return self._obs()

    def _obs(self) -> Dict[str, Any]:
        low, high = self._regime_params(self.regime_id)
        obs_val = self.rng.randint(low, high)
        return {"obs": obs_val, "t": self.t, "regime": self.regime_id}

    def step(self, action: int) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        action = int(action) & 1
        correct = 1 if self.true_polarity > 0 else 0
        reward = 1.0 if action == correct else -1.0
        self.total_reward += reward
        self.t += 1

        if self.t % self.regime_len == 0 and self.t < self.horizon:
            self.regime_id += 1

        if self.t < self.horizon and self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1
            for _ in range(5):
                self.chi.reveal(0.50)

        if self.t >= self.horizon:
            self.done = True

        self.chi.reveal(0.18)

        info = {
            "true_polarity": self.true_polarity,
            "flip_count": self.flip_count,
            "chi": self.chi.chi,
            "polarity": self.chi.polarity(),
            "r_chi": self.chi.peek(),
            "safe_token": self.chi.safe_token(include_r=True),
            "regime": self.regime_id,
            "is_reducible": False if self.flip_count % 2 == 1 else True,
        }
        return self._obs(), reward, self.done, info


def agent_reactive(obs, history, info):
    return int(obs.get("obs", 0)) & 1

def agent_visible_history(obs, history, info):
    if not history:
        return 0
    votes = sum(int(h.get("obs", 0)) & 1 for h in history[-12:])
    return 1 if votes > len(history[-12:]) / 2 else 0

class AdaptiveEMA:
    def __init__(self, alpha=0.22):
        self.alpha = alpha
        self.ema = 0.5
    def __call__(self, obs, history, info):
        bit = int(obs.get("obs", 0)) & 1
        self.ema = (1 - self.alpha) * self.ema + self.alpha * bit
        return 1 if self.ema > 0.5 else 0

class AdaptiveBayes:
    def __init__(self):
        self.alpha = 1.0
        self.beta = 1.0
    def __call__(self, obs, history, info):
        bit = int(obs.get("obs", 0)) & 1
        if bit == 1: self.alpha += 1
        else: self.beta += 1
        return 1 if self.alpha / (self.alpha + self.beta) > 0.5 else 0

class AdaptiveRegimeAware:
    def __init__(self):
        self.per_regime = {}
        self.counts = {}
    def __call__(self, obs, history, info):
        rid = int(obs.get("regime", 0))
        bit = float(int(obs.get("obs", 0)) & 1)
        if rid not in self.per_regime:
            self.per_regime[rid] = 0.5
            self.counts[rid] = 0
        n = self.counts[rid]
        self.per_regime[rid] = (self.per_regime[rid] * n + bit) / (n + 1)
        self.counts[rid] = n + 1
        return 1 if self.per_regime[rid] > 0.5 else 0

def agent_full_chi(obs, history, info):
    pol = info.get("polarity")
    if pol is not None:
        return 1 if pol > 0 else 0
    return 1 if info.get("r_chi", 0.0) > 0 else 0

def agent_frozen_chi(obs, history, info, frozen_value=0):
    return int(frozen_value)

def agent_no_reveal(obs, history, info):
    return agent_visible_history(obs, history, info)

def make_adaptive_agent(cls, **kwargs):
    def agent_fn(obs, history, info, _state={"agent": None}):
        if not history:
            _state["agent"] = cls(**kwargs)
        return _state["agent"](obs, history, info)
    return agent_fn

def run_episode(env, agent_fn, seed, *, frozen_value=0, agent_name=""):
    obs = env.reset(seed=seed)
    history = []
    info = {"polarity": env.chi.polarity(), "r_chi": env.chi.peek()}
    done = False
    while not done:
        if agent_name == "frozen":
            action = agent_fn(obs, history, info, frozen_value=frozen_value)
        else:
            action = agent_fn(obs, history, info)
        history.append(dict(obs))
        obs, reward, done, info = env.step(action)
    return env.total_reward, env.flip_count

def evaluate(agent_fn, n_episodes=60, horizon=80, flip_prob=0.12, base_seed=0, *, frozen_value=0, agent_name=""):
    total_ret = 0.0
    total_flips = 0
    for i in range(n_episodes):
        env = HardRegimeShift(horizon=horizon, flip_prob=flip_prob, seed=base_seed + i)
        ret, flips = run_episode(env, agent_fn, seed=base_seed + i, frozen_value=frozen_value, agent_name=agent_name)
        total_ret += ret
        total_flips += flips
    return total_ret / n_episodes, total_flips / n_episodes

if __name__ == "__main__":
    print("=" * 72)
    print("COMMITMENT STRESS SUITE — Hard Regime-Shift variant")
    print("=" * 72)
    print("Horizon=80  flip_prob=0.12  regime_len=16  Episodes=60")
    print("Max possible return = 80")
    print()
    results = {}
    flips = {}
    results["Reactive"], flips["Reactive"] = evaluate(agent_reactive, agent_name="reactive")
    results["Visible-history"], flips["Visible-history"] = evaluate(agent_visible_history, agent_name="visible")
    results["Adaptive EMA"], flips["Adaptive EMA"] = evaluate(make_adaptive_agent(AdaptiveEMA), agent_name="ema")
    results["Adaptive Bayes"], flips["Adaptive Bayes"] = evaluate(make_adaptive_agent(AdaptiveBayes), agent_name="bayes")
    results["Adaptive RegimeAware"], flips["Adaptive RegimeAware"] = evaluate(make_adaptive_agent(AdaptiveRegimeAware), agent_name="regime")
    results["Full χ + reveal"], flips["Full χ + reveal"] = evaluate(agent_full_chi, agent_name="full")
    results["Frozen χ=0"], flips["Frozen χ=0"] = evaluate(agent_frozen_chi, frozen_value=0, agent_name="frozen")
    results["Frozen χ=1"], flips["Frozen χ=1"] = evaluate(agent_frozen_chi, frozen_value=1, agent_name="frozen")
    results["χ, no reveal"], flips["χ, no reveal"] = evaluate(agent_no_reveal, agent_name="no_reveal")
    print(f"{'Method':<26} {'Avg return':>10}  {'Avg flips':>9}  Notes")
    print("-" * 72)
    notes = {
        "Reactive": "obs noise only",
        "Visible-history": "window majority",
        "Adaptive EMA": "online EMA",
        "Adaptive Bayes": "Beta belief",
        "Adaptive RegimeAware": "per-regime estimate (still pure-visible)",
        "Full χ + reveal": "tracks polarity via r_χ",
        "Frozen χ=0": "stuck",
        "Frozen χ=1": "stuck",
        "χ, no reveal": "falls back to visible",
    }
    for name, ret in results.items():
        print(f"{name:<26} {ret:>+10.2f}  {flips[name]:>9.1f}  {notes.get(name, '')}")
    print("-" * 72)
    full = results["Full χ + reveal"]
    for name in ["Visible-history", "Adaptive EMA", "Adaptive Bayes", "Adaptive RegimeAware", "Reactive"]:
        print(f"Gap (Full − {name}): {full - results[name]:+.2f}")
    from chi_primitive import demonstrate_parity_trap
    demo = demonstrate_parity_trap()
    print()
    print(f"is_reducible after odd commits: {demo['is_reducible']}  (claim_holds={demo['claim_holds']})")
    assert demo["claim_holds"]
    assert full > results["Visible-history"] + 10.0
    assert full > results["Adaptive RegimeAware"] + 10.0
    print()
    print("OK — Hard Regime-Shift separation is decisive (incl. regime-aware adaptive)")
