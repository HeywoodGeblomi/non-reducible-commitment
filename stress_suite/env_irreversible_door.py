#!/usr/bin/env python3
"""Environment 1 — Irreversible Door"""
from __future__ import annotations
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chi_primitive"))
from chi_primitive import ChiState, demonstrate_parity_trap

class IrreversibleDoor:
    def __init__(self, horizon: int = 12, seed: int = 42):
        self.horizon = horizon
        self.rng = random.Random(seed)
        self.reset()

    def reset(self, seed=None):
        if seed is not None:
            self.rng = random.Random(seed)
        self.t = 0
        self.true_door = None
        self.chi = ChiState(chi=1)
        self.done = False
        self.total_reward = 0.0
        for _ in range(5):
            self.chi.reveal(0.35)
        return {"phase": "choose", "obs": 0}

    def step(self, action: int):
        action = int(action) & 1
        reward = 0.0
        if self.t == 0:
            self.true_door = action
            self.chi.force(action)
            for _ in range(5):
                self.chi.reveal(0.40)
        else:
            correct = self.true_door
            reward = 1.0 if action == correct else -1.0
        self.total_reward += reward
        self.t += 1
        self.chi.reveal(0.20)
        if self.t >= self.horizon:
            self.done = True
        obs = {"phase": "act", "obs": self.rng.randint(0, 1)} if self.true_door is not None else {"phase": "choose", "obs": 0}
        info = {
            "true_door": self.true_door,
            "polarity": self.chi.polarity(),
            "r_chi": self.chi.peek(),
        }
        return obs, reward, self.done, info

def agent_reactive(obs, history, info):
    return int(obs.get("obs", 0)) & 1

def agent_visible(obs, history, info):
    if not history:
        return 0
    return 1 if sum(h.get("obs", 0) & 1 for h in history) > len(history) / 2 else 0

def agent_full(obs, history, info):
    if obs.get("phase") == "choose":
        return random.randint(0, 1)
    pol = info.get("polarity")
    if pol is not None:
        return 1 if pol > 0 else 0
    return 1 if info.get("r_chi", 0) > 0 else 0

def agent_frozen(obs, history, info, frozen=0):
    if obs.get("phase") == "choose":
        return frozen
    return int(frozen)

def evaluate(agent_fn, n=80, frozen=None, name=""):
    total = 0.0
    for i in range(n):
        env = IrreversibleDoor(seed=i)
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
    return total / n

if __name__ == "__main__":
    print("=" * 60)
    print("Env 1: Irreversible Door  (horizon=12, episodes=80)")
    print("=" * 60)
    results = {
        "Reactive": evaluate(agent_reactive),
        "Visible-history": evaluate(agent_visible),
        "Full χ + reveal": evaluate(agent_full),
        "Frozen χ=0": evaluate(agent_frozen, frozen=0, name="frozen"),
        "Frozen χ=1": evaluate(agent_frozen, frozen=1, name="frozen"),
    }
    print(f"{'Method':<22} {'Avg return':>10}")
    print("-" * 60)
    for k, v in results.items():
        print(f"{k:<22} {v:>+10.2f}")
    print("-" * 60)
    print(f"Gap (Full - Visible): {results['Full χ + reveal'] - results['Visible-history']:+.2f}")
    demo = demonstrate_parity_trap()
    print(f"is_reducible after odd commits: {demo['is_reducible']} (claim_holds={demo['claim_holds']})")
    assert demo["claim_holds"]
    assert results["Full χ + reveal"] > results["Visible-history"] + 2
    print("OK — Irreversible Door separation is decisive")
