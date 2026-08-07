#!/usr/bin/env python3
"""Environment 3 — Commitment-Gated Reconstruction"""
from __future__ import annotations
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chi_primitive"))
from chi_primitive import ChiState, demonstrate_parity_trap

class CommitmentGatedReconstruction:
    def __init__(self, horizon: int = 16, flip_prob: float = 0.15, seed: int = 42):
        self.horizon = horizon
        self.flip_prob = flip_prob
        self.rng = random.Random(seed)
        self._last_draft = {}
        self.reset()

    def reset(self, seed=None):
        if seed is not None:
            self.rng = random.Random(seed)
        self.t = 0
        self.chi = ChiState(chi=1)
        self.true_polarity = 1.0
        self.done = False
        self.total_reward = 0.0
        self.flip_count = 0
        for _ in range(5):
            self.chi.reveal(0.35)
        return self._obs_store()

    def _generate_draft(self):
        draft_action = self.rng.randint(0, 1)
        needed = 1 if self.true_polarity > 0 else 0
        return {"draft_action": draft_action, "aligned": draft_action == needed}

    def _obs_store(self):
        o = {"t": self.t, "obs": self.rng.randint(0, 2), "draft": self._generate_draft()}
        self._last_draft = o["draft"]
        return o

    def step(self, action: int):
        action = int(action) & 1
        draft = self._last_draft
        if action == 1:
            reward = 1.0 if draft["aligned"] else -1.5
        else:
            reward = 0.4 if not draft["aligned"] else -0.8
        self.total_reward += reward
        self.t += 1
        if self.t < self.horizon and self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1
            for _ in range(4):
                self.chi.reveal(0.45)
        if self.t >= self.horizon:
            self.done = True
        self.chi.reveal(0.20)
        next_obs = self._obs_store()
        info = {
            "true_polarity": self.true_polarity,
            "flip_count": self.flip_count,
            "polarity": self.chi.polarity(),
            "r_chi": self.chi.peek(),
            "is_reducible": False if self.flip_count % 2 == 1 else True,
        }
        return next_obs, reward, self.done, info

def agent_reactive(obs, history, info):
    return 1  # always ACCEPT

def agent_visible(obs, history, info):
    draft = obs.get("draft") or {}
    return 1 if draft.get("draft_action", 0) == 1 else 0

def agent_full(obs, history, info):
    draft = obs.get("draft") or {}
    draft_action = draft.get("draft_action", 0)
    pol = info.get("polarity")
    if pol is None:
        pol = 1.0 if info.get("r_chi", 0) > 0 else -1.0
    needed = 1 if pol > 0 else 0
    return 1 if draft_action == needed else 0

def agent_frozen(obs, history, info, frozen=0):
    draft = obs.get("draft") or {}
    return 1 if draft.get("draft_action", 0) == int(frozen) else 0

def evaluate(agent_fn, n=80, frozen=None, name=""):
    total, flips = 0.0, 0
    for i in range(n):
        env = CommitmentGatedReconstruction(seed=i)
        obs = env.reset(seed=i)
        history, info, done = [], {"polarity": env.chi.polarity(), "r_chi": env.chi.peek()}, False
        while not done:
            if name == "frozen":
                action = agent_fn(obs, history, info, frozen=frozen)
            else:
                action = agent_fn(obs, history, info)
            history.append(dict(obs))
            obs, reward, done, info = env.step(action)
        total += env.total_reward
        flips += env.flip_count
    return total / n, flips / n

if __name__ == "__main__":
    print("=" * 60)
    print("Env 3: Commitment-Gated Reconstruction  (horizon=16, episodes=80)")
    print("=" * 60)
    results = {}
    for name, fn, kw in [
        ("Reactive (always ACCEPT)", agent_reactive, {}),
        ("Visible-history", agent_visible, {}),
        ("Full χ + reveal", agent_full, {}),
        ("Frozen χ=0", agent_frozen, {"frozen": 0, "name": "frozen"}),
        ("Frozen χ=1", agent_frozen, {"frozen": 1, "name": "frozen"}),
    ]:
        ret, fl = evaluate(fn, **kw)
        results[name] = ret
        print(f"{name:<28} {ret:>+10.2f}  (avg flips={fl:.1f})")
    print("-" * 60)
    print(f"Gap (Full - Visible): {results['Full χ + reveal'] - results['Visible-history']:+.2f}")
    demo = demonstrate_parity_trap()
    print(f"is_reducible after odd commits: {demo['is_reducible']} (claim_holds={demo['claim_holds']})")
    assert demo["claim_holds"]
    assert results["Full χ + reveal"] > results["Visible-history"] + 1.5
    print("OK — Commitment-Gated Reconstruction separation is decisive")
