#!/usr/bin/env python3
"""
E* — Controlled stress that escapes pure observational equivalence

Design goal
-----------
An irreversible early commitment still exists and determines later optimal
behaviour after odd flips. The observation process is *not* informationally
independent of χ: a weak, noisy, non-stationary residual correlates with
polarity. Strong laptop-runnable latent-state / belief-tracking baselines
(simple Bayesian filter, EMA latent, fixed residual buffer) still fail to
maintain the correct parity over long horizons under realistic noise and
regime drift. Pure χ + reveal recovers near-ceiling performance with a
clear gap.

This is still a controlled stress test. It does not claim membership of
real agent trajectories in P_parity, nor that χ is necessary outside the
engineered settings examined here.

Horizon ≥ 80, ≈ 8–12 irreversible flips.
Everything runs on CPU.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chi_primitive import ChiState


class EscapeObservationalEquivalence:
    """
    Horizon H ≈ 90.
    Hidden polarity flips at random intervals.
    Observations contain a weak residual:
        residual = polarity * signal_strength + N(0, noise)
    where signal_strength itself drifts and occasionally reverses
    (independent of χ). This breaks pure informational independence
    while remaining hard for ordinary latent-state trackers.
    Reward = +1 if action matches current polarity else −1.
    """

    def __init__(
        self,
        horizon: int = 90,
        flip_prob: float = 0.11,
        base_snr: float = 0.22,
        noise_std: float = 1.0,
        drift_scale: float = 0.04,
        bias_flip_prob: float = 0.04,
        seed: int = 42,
    ):
        self.horizon = int(horizon)
        self.flip_prob = float(flip_prob)
        self.base_snr = float(base_snr)
        self.noise_std = float(noise_std)
        self.drift_scale = float(drift_scale)
        self.bias_flip_prob = float(bias_flip_prob)
        self.rng = random.Random(seed)
        self.reset(seed=seed)

    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        if seed is not None:
            self.rng = random.Random(seed)
        self.t = 0
        self.chi = ChiState(chi=1)
        self.true_polarity = 1.0
        self.done = False
        self.total_reward = 0.0
        self.flip_count = 0
        self.signal_strength = self.base_snr
        self.bias_sign = 1.0
        for _ in range(6):
            self.chi.reveal(0.40)
        return self._obs()

    def _obs(self) -> Dict[str, Any]:
        residual = (
            self.true_polarity * self.signal_strength * self.bias_sign
            + self.rng.gauss(0.0, self.noise_std)
        )
        coarse = 1 if residual > 0 else 0
        return {
            "residual": residual,
            "obs": coarse,
            "t": self.t,
            "signal_strength": self.signal_strength,
        }

    def step(self, action: int) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        action = int(action) & 1
        correct = 1 if self.true_polarity > 0 else 0
        reward = 1.0 if action == correct else -1.0
        self.total_reward += reward
        self.t += 1

        self.signal_strength += self.rng.gauss(0.0, self.drift_scale)
        self.signal_strength = max(0.05, min(0.55, self.signal_strength))
        if self.rng.random() < self.bias_flip_prob:
            self.bias_sign *= -1.0

        if self.t < self.horizon and self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1
            for _ in range(5):
                self.chi.reveal(0.45)

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
            "is_reducible": False if self.flip_count % 2 == 1 else True,
            "bias_sign": self.bias_sign,
            "signal_strength": self.signal_strength,
        }
        return self._obs(), reward, self.done, info


def agent_reactive(obs, history, info):
    return int(obs.get("obs", 0))

def agent_visible_history(obs, history, info):
    if not history:
        return 0
    votes = sum(int(h.get("obs", 0)) for h in history[-15:])
    return 1 if votes > len(history[-15:]) / 2 else 0

class AdaptiveEMA:
    def __init__(self, alpha=0.18):
        self.alpha = alpha
        self.ema = 0.0
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.ema = (1 - self.alpha) * self.ema + self.alpha * r
        return 1 if self.ema > 0 else 0

class BayesianFilter:
    def __init__(self, prior_var=1.0, noise_var=1.0):
        self.noise_var = noise_var
        self.log_odds = 0.0
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        ll1 = -0.5 * (r - 0.3) ** 2 / self.noise_var
        ll0 = -0.5 * (r + 0.3) ** 2 / self.noise_var
        self.log_odds += (ll1 - ll0)
        self.log_odds *= 0.97
        return 1 if self.log_odds > 0 else 0

class FixedBufferLatent:
    def __init__(self, buf_size=12):
        self.buf_size = buf_size
        self.buf = []
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.buf.append(r)
        if len(self.buf) > self.buf_size:
            self.buf = self.buf[-self.buf_size:]
        if not self.buf:
            return 0
        w = [0.5 + 0.5 * (i / len(self.buf)) for i in range(len(self.buf))]
        s = sum(w)
        avg = sum(x * wi for x, wi in zip(self.buf, w)) / s
        return 1 if avg > 0 else 0

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

def evaluate(agent_fn, n_episodes=50, horizon=90, flip_prob=0.11, base_seed=0, *, frozen_value=0, agent_name=""):
    total_ret = 0.0
    total_flips = 0
    for i in range(n_episodes):
        env = EscapeObservationalEquivalence(horizon=horizon, flip_prob=flip_prob, seed=base_seed + i)
        ret, flips = run_episode(env, agent_fn, seed=base_seed + i, frozen_value=frozen_value, agent_name=agent_name)
        total_ret += ret
        total_flips += flips
    return total_ret / n_episodes, total_flips / n_episodes

if __name__ == "__main__":
    print("=" * 74)
    print("E* — Escape pure observational equivalence (controlled stress)")
    print("=" * 74)
    print("Horizon=90  flip_prob=0.11  base_snr=0.22  Episodes=50")
    print("Max possible return = 90")
    print("Disclaimer: controlled stress; does not claim real-agent membership.")
    print()
    results = {}
    flips = {}
    results["Reactive"], flips["Reactive"] = evaluate(agent_reactive, agent_name="reactive")
    results["Visible-history"], flips["Visible-history"] = evaluate(agent_visible_history, agent_name="visible")
    results["Adaptive EMA"], flips["Adaptive EMA"] = evaluate(make_adaptive_agent(AdaptiveEMA), agent_name="ema")
    results["Bayesian Filter"], flips["Bayesian Filter"] = evaluate(make_adaptive_agent(BayesianFilter), agent_name="bayes")
    results["FixedBuffer Latent"], flips["FixedBuffer Latent"] = evaluate(make_adaptive_agent(FixedBufferLatent, buf_size=12), agent_name="buffer")
    results["Full χ + reveal"], flips["Full χ + reveal"] = evaluate(agent_full_chi, agent_name="full")
    results["Frozen χ=0"], flips["Frozen χ=0"] = evaluate(agent_frozen_chi, frozen_value=0, agent_name="frozen")
    results["Frozen χ=1"], flips["Frozen χ=1"] = evaluate(agent_frozen_chi, frozen_value=1, agent_name="frozen")
    results["χ, no reveal"], flips["χ, no reveal"] = evaluate(agent_no_reveal, agent_name="no_reveal")
    print(f"{'Method':<22} {'Avg return':>10}  {'Avg flips':>9}  Notes")
    print("-" * 74)
    notes = {
        "Reactive": "coarse obs only",
        "Visible-history": "window majority",
        "Adaptive EMA": "EMA on residual",
        "Bayesian Filter": "latent-state Bayesian (uses residual)",
        "FixedBuffer Latent": "fixed residual buffer + readout",
        "Full χ + reveal": "tracks polarity via r_χ",
        "Frozen χ=0": "stuck",
        "Frozen χ=1": "stuck",
        "χ, no reveal": "falls back to visible",
    }
    for name, ret in results.items():
        print(f"{name:<22} {ret:>+10.2f}  {flips[name]:>9.1f}  {notes.get(name, '')}")
    print("-" * 74)
    full = results["Full χ + reveal"]
    for name in ["Visible-history", "Adaptive EMA", "Bayesian Filter", "FixedBuffer Latent", "Reactive"]:
        print(f"Gap (Full − {name}): {full - results[name]:+.2f}")
    from chi_primitive import demonstrate_parity_trap
    demo = demonstrate_parity_trap()
    print()
    print(f"is_reducible (parity-trap helper): {demo['is_reducible']}  (claim_holds={demo['claim_holds']})")
    print()
    assert full > results["Bayesian Filter"] + 5.0
    assert full > results["FixedBuffer Latent"] + 5.0
    print("OK — E* shows separation against latent-state baselines under weak residual")
    print("    (controlled stress; pure observational equivalence has been escaped)")
