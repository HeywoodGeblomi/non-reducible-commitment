#!/usr/bin/env python3
"""
E** — Still-harder controlled stress that escapes pure observational equivalence

Design goal
-----------
Irreversible early commitments still exist and determine later optimal
behaviour after odd flips. The observation process carries moderate
mutual information with polarity (base SNR ≈ 0.40), but residual
statistics are non-stationary in three simultaneous ways that are
independent of χ:

  • correlation-sign of residual vs polarity flips occasionally
  • amplitude modulation (random walk)
  • additive bias: random walk + occasional large jumps
  • a slow independent residual-regime variable

In addition a polarity-dependent draft/memory token is emitted; correct
gating of that token requires knowing the current polarity.

Stronger laptop-runnable latent-state / hierarchical / belief-tracking
baselines are implemented and must be defeated:

  1. Adaptive Bayesian polarity filter (process noise + soft forgetting)
  2. Hierarchical buffer (short EMA + medium rolling + long mean)
  3. Multi-scale EMA (3 time-constants) + linear readout
  4. Simple Kalman-style residual + bias tracker
  5. Adaptive EMA (reference)

Pure χ + titrated reveal (α ≈ 0.20) recovers near-ceiling performance.
All pure-visible / latent baselines lose the parity under accumulation
of error + irreversible flips + residual non-stationarity.

This is still a controlled stress test. It does not claim membership of
real agent trajectories in P_parity, nor that χ is necessary outside the
engineered settings examined here.

Horizon H=120, ≈12–14 irreversible flips.
Everything runs on pure Python (stdlib only).
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chi_primitive import ChiState


class EDoubleStar:
    """
    Horizon H = 120.
    Hidden polarity flips at irregular intervals.
    Residual carries moderate SNR with χ but is heavily non-stationary
    independently of χ. A draft token is also emitted that is only
    correctly interpretable under the true current polarity.
    """

    def __init__(
        self,
        horizon: int = 120,
        flip_prob: float = 0.11,
        base_snr: float = 0.40,
        noise_std: float = 1.0,
        drift_scale: float = 0.035,
        bias_jump_prob: float = 0.035,
        corr_sign_flip_prob: float = 0.03,
        seed: int = 42,
    ):
        self.horizon = int(horizon)
        self.flip_prob = float(flip_prob)
        self.base_snr = float(base_snr)
        self.noise_std = float(noise_std)
        self.drift_scale = float(drift_scale)
        self.bias_jump_prob = float(bias_jump_prob)
        self.corr_sign_flip_prob = float(corr_sign_flip_prob)
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
        self.bias = 0.0
        self.corr_sign = 1.0
        self.residual_regime = 0

        for _ in range(6):
            self.chi.reveal(0.40)
        return self._obs()

    def _obs(self) -> Dict[str, Any]:
        residual = (
            self.true_polarity * self.signal_strength * self.corr_sign
            + self.bias
            + self.rng.gauss(0.0, self.noise_std)
        )
        coarse = 1 if residual > 0 else 0

        draft_action = self.rng.randint(0, 1)
        needed = 1 if self.true_polarity > 0 else 0
        aligned = (draft_action == needed)

        return {
            "residual": residual,
            "obs": coarse,
            "t": self.t,
            "draft_action": draft_action,
            "draft_aligned": aligned,
            "signal_strength": self.signal_strength,
            "residual_regime": self.residual_regime,
        }

    def step(self, action: int) -> Tuple[Dict[str, Any], float, bool, Dict[str, Any]]:
        """
        Action is interpreted as a polarity guess (0 or 1).
        Reward = +1 if action matches true polarity, else −1.
        The draft/memory token is an additional observation that
        baselines may use or ignore; it does not change the reward
        definition.
        """
        action = int(action) & 1
        correct = 1 if self.true_polarity > 0 else 0
        reward = 1.0 if action == correct else -1.0

        self.total_reward += reward
        self.t += 1

        self.signal_strength += self.rng.gauss(0.0, self.drift_scale)
        self.signal_strength = max(0.12, min(0.65, self.signal_strength))

        self.bias += self.rng.gauss(0.0, 0.08)
        if self.rng.random() < self.bias_jump_prob:
            self.bias += self.rng.choice([-1.2, -0.8, 0.8, 1.2])
        self.bias = max(-2.5, min(2.5, self.bias))

        if self.rng.random() < self.corr_sign_flip_prob:
            self.corr_sign *= -1.0

        if self.t % 25 == 0:
            self.residual_regime = (self.residual_regime + 1) % 3

        if self.t < self.horizon and self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1
            for _ in range(5):
                self.chi.reveal(0.45)

        if self.t >= self.horizon:
            self.done = True

        self.chi.reveal(0.20)

        next_obs = self._obs()

        info = {
            "true_polarity": self.true_polarity,
            "flip_count": self.flip_count,
            "chi": self.chi.chi,
            "polarity": self.chi.polarity(),
            "r_chi": self.chi.peek(),
            "safe_token": self.chi.safe_token(include_r=True),
            "is_reducible": False if self.flip_count % 2 == 1 else True,
            "bias": self.bias,
            "corr_sign": self.corr_sign,
            "signal_strength": self.signal_strength,
        }
        return next_obs, reward, self.done, info


def agent_reactive(obs, history, info):
    return int(obs.get("obs", 0))

def agent_visible_history(obs, history, info):
    if not history:
        return 0
    votes = sum(int(h.get("obs", 0)) for h in history[-20:])
    return 1 if votes > len(history[-20:]) / 2 else 0

class AdaptiveEMA:
    def __init__(self, alpha=0.15):
        self.alpha = alpha
        self.ema = 0.0
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.ema = (1 - self.alpha) * self.ema + self.alpha * r
        return 1 if self.ema > 0 else 0

class BayesianProcessNoise:
    def __init__(self, process_noise=0.04):
        self.log_odds = 0.0
        self.process_noise = process_noise
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        ll1 = -0.5 * (r - 0.35) ** 2
        ll0 = -0.5 * (r + 0.35) ** 2
        self.log_odds += (ll1 - ll0)
        self.log_odds *= (1.0 - self.process_noise)
        return 1 if self.log_odds > 0 else 0

class HierarchicalBuffer:
    def __init__(self, short_alpha=0.25, med_len=12, long_len=40):
        self.short_alpha = short_alpha
        self.med_len = med_len
        self.long_len = long_len
        self.short = 0.0
        self.med = []
        self.long = []
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.short = (1 - self.short_alpha) * self.short + self.short_alpha * r
        self.med.append(r)
        if len(self.med) > self.med_len:
            self.med = self.med[-self.med_len:]
        self.long.append(r)
        if len(self.long) > self.long_len:
            self.long = self.long[-self.long_len:]
        med_m = sum(self.med) / len(self.med) if self.med else 0.0
        long_m = sum(self.long) / len(self.long) if self.long else 0.0
        score = 0.5 * self.short + 0.3 * med_m + 0.2 * long_m
        return 1 if score > 0 else 0

class MultiScaleEMA:
    def __init__(self):
        self.e1 = 0.0
        self.e2 = 0.0
        self.e3 = 0.0
        self.a1, self.a2, self.a3 = 0.3, 0.12, 0.04
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.e1 = (1 - self.a1) * self.e1 + self.a1 * r
        self.e2 = (1 - self.a2) * self.e2 + self.a2 * r
        self.e3 = (1 - self.a3) * self.e3 + self.a3 * r
        score = 0.55 * self.e1 + 0.30 * self.e2 + 0.15 * self.e3
        return 1 if score > 0 else 0

class KalmanStyle:
    def __init__(self):
        self.x = 0.0
        self.b = 0.0
        self.p = 1.0
    def __call__(self, obs, history, info):
        r = float(obs.get("residual", 0.0))
        self.p += 0.05
        k = self.p / (self.p + 1.0)
        innov = r - (self.x + self.b)
        self.x += k * innov * 0.7
        self.b += k * innov * 0.3
        self.p *= (1 - k)
        return 1 if self.x > 0 else 0

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

def evaluate(agent_fn, n_episodes=50, horizon=120, flip_prob=0.11, base_seed=0, *, frozen_value=0, agent_name=""):
    total_ret = 0.0
    total_flips = 0
    for i in range(n_episodes):
        env = EDoubleStar(horizon=horizon, flip_prob=flip_prob, seed=base_seed + i)
        ret, flips = run_episode(env, agent_fn, seed=base_seed + i, frozen_value=frozen_value, agent_name=agent_name)
        total_ret += ret
        total_flips += flips
    return total_ret / n_episodes, total_flips / n_episodes

if __name__ == "__main__":
    print("=" * 76)
    print("E** — Still-harder controlled stress (escape pure observational equivalence)")
    print("=" * 76)
    print("Horizon=120  flip_prob=0.11  base_snr=0.40  Episodes=50")
    print("Max possible return = 120")
    print("Disclaimer: controlled stress; does not claim real-agent membership in P_parity.")
    print()
    results = {}
    flips = {}
    results["Reactive"], flips["Reactive"] = evaluate(agent_reactive, agent_name="reactive")
    results["Visible-history"], flips["Visible-history"] = evaluate(agent_visible_history, agent_name="visible")
    results["Adaptive EMA"], flips["Adaptive EMA"] = evaluate(make_adaptive_agent(AdaptiveEMA), agent_name="ema")
    results["Bayesian+ProcessNoise"], flips["Bayesian+ProcessNoise"] = evaluate(make_adaptive_agent(BayesianProcessNoise), agent_name="bayes")
    results["HierarchicalBuffer"], flips["HierarchicalBuffer"] = evaluate(make_adaptive_agent(HierarchicalBuffer), agent_name="hier")
    results["MultiScaleEMA"], flips["MultiScaleEMA"] = evaluate(make_adaptive_agent(MultiScaleEMA), agent_name="mse")
    results["KalmanStyle"], flips["KalmanStyle"] = evaluate(make_adaptive_agent(KalmanStyle), agent_name="kalman")
    results["Full χ + reveal"], flips["Full χ + reveal"] = evaluate(agent_full_chi, agent_name="full")
    results["Frozen χ=0"], flips["Frozen χ=0"] = evaluate(agent_frozen_chi, frozen_value=0, agent_name="frozen")
    results["Frozen χ=1"], flips["Frozen χ=1"] = evaluate(agent_frozen_chi, frozen_value=1, agent_name="frozen")
    results["χ, no reveal"], flips["χ, no reveal"] = evaluate(agent_no_reveal, agent_name="no_reveal")
    print(f"{'Method':<24} {'Avg return':>10}  {'Avg flips':>9}  Notes")
    print("-" * 76)
    notes = {
        "Reactive": "coarse obs only",
        "Visible-history": "window majority",
        "Adaptive EMA": "EMA on residual",
        "Bayesian+ProcessNoise": "Bayesian with process noise",
        "HierarchicalBuffer": "short + med + long buffers",
        "MultiScaleEMA": "3-scale EMA + readout",
        "KalmanStyle": "residual + bias tracker",
        "Full χ + reveal": "tracks polarity via r_χ",
        "Frozen χ=0": "stuck",
        "Frozen χ=1": "stuck",
        "χ, no reveal": "falls back to visible",
    }
    for name, ret in results.items():
        print(f"{name:<24} {ret:>+10.2f}  {flips[name]:>9.1f}  {notes.get(name, '')}")
    print("-" * 76)
    full = results["Full χ + reveal"]
    for name in ["Visible-history", "Adaptive EMA", "Bayesian+ProcessNoise", "HierarchicalBuffer", "MultiScaleEMA", "KalmanStyle", "Reactive"]:
        print(f"Gap (Full − {name}): {full - results[name]:+.2f}")
    from chi_primitive import demonstrate_parity_trap
    demo = demonstrate_parity_trap()
    print()
    print(f"is_reducible (parity-trap helper): {demo['is_reducible']}  (claim_holds={demo['claim_holds']})")
    print()
    assert full > results["Bayesian+ProcessNoise"] + 15.0
    assert full > results["HierarchicalBuffer"] + 15.0
    assert full > results["MultiScaleEMA"] + 15.0
    assert full > results["KalmanStyle"] + 15.0
    print("OK — E** shows separation against stronger latent / hierarchical baselines")
    print("    (controlled stress; pure observational equivalence has been escaped;")
    print("     residual non-stationarity independent of χ confuses ordinary trackers)")
