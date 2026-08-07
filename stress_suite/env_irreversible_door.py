#!/usr/bin/env python3
"""Environment 1 — Irreversible Door (correct frozen ablation)."""
from __future__ import annotations
import random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chi_primitive"))
from chi_primitive import ChiState, demonstrate_parity_trap

class IrreversibleDoor:
    def __init__(self, horizon=12, seed=42):
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

    def step(self, action):
        action = int(action) & 1
        reward = 0.0
        if self.t == 0:
            self.true_door = action
            self.chi.force(action)
            for _ in range(5):
                self.chi.reveal(0.40)
        else:
            reward = 1.0 if action == self.true_door else -1.0
        self.total_reward += reward
        self.t += 1
        self.chi.reveal(0.20)
        if self.t >= self.horizon:
            self.done = True
        obs = {"phase": "act", "obs": self.rng.randint(0, 1)} if self.true_door is not None else {"phase": "choose", "obs": 0}
        info = {"true_door": self.true_door, "polarity": self.chi.polarity(), "r_chi": self.chi.peek()}
        return obs, reward, self.done, info

def agent_reactive(obs, history, info):
    if obs.get("phase") == "choose":
        return random.randint(0, 1)
    return int(obs.get("obs", 0)) & 1

def agent_visible(obs, history, info):
    if obs.get("phase") == "choose":
        return random.randint(0, 1)
    acts = [h.get("obs", 0) & 1 for h in history if h.get("phase") == "act"]
    return 0 if not acts else (1 if sum(acts) > len(acts) / 2 else 0)

def agent_full(obs, history, info):
    if obs.get("phase") == "choose":
        return random.randint(0, 1)
    pol = info.get("polarity")
    if pol is not None:
        return 1 if pol > 0 else 0
    return 1 if info.get("r_chi", 0) > 0 else 0

def evaluate(agent_fn, n=80, freeze_to=None):
    total = 0.0
    for i in range(n):
        env = IrreversibleDoor(seed=i)
        obs = env.reset(seed=i)
        history, info, done = [], {"polarity": env.chi.polarity(), "r_chi": env.chi.peek()}, False
        while not done:
            action = agent_fn(obs, history, info)
            history.append(dict(obs))
            obs, reward, done, info = env.step(action)
            if freeze_to is not None and env.t == 1:
                env.chi.force(int(freeze_to))
                for _ in range(5):
                    env.chi.reveal(0.40)
                info = {"true_door": env.true_door, "polarity": env.chi.polarity(), "r_chi": env.chi.peek()}
        total += env.total_reward
    return total / n

if __name__ == "__main__":
    print("=" * 60)
    print("Env 1: Irreversible Door  (horizon=12, episodes=80)")
    print("=" * 60)
    results = {
        "Reactive": evaluate(agent_reactive),
        "Visible-history": evaluate(agent_visible),
        "Full chi + reveal": evaluate(agent_full),
        "Frozen chi=0": evaluate(agent_full, freeze_to=0),
        "Frozen chi=1": evaluate(agent_full, freeze_to=1),
    }
    print(f"{'Method':<22} {'Avg return':>10}")
    print("-" * 60)
    for k, v in results.items():
        print(f"{k:<22} {v:>+10.2f}")
    print("-" * 60)
    gap = results["Full chi + reveal"] - results["Visible-history"]
    print(f"Gap (Full - Visible): {gap:+.2f}")
    demo = demonstrate_parity_trap()
    print(f"is_reducible after odd commits: {demo['is_reducible']} (claim_holds={demo['claim_holds']})")
    assert demo["claim_holds"]
    assert results["Full chi + reveal"] > results["Visible-history"] + 2
    frozen_best = max(results["Frozen chi=0"], results["Frozen chi=1"])
    assert results["Full chi + reveal"] > frozen_best + 1.0
    print("OK — Irreversible Door separation is decisive")
