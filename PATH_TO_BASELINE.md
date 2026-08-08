# Path to Official Long-Horizon Agent Baselines

**Status:** Open gate (hardware-blocked in current agent sandbox).  
Companion to FORMAL_CLAIM.md v0.1 and the pure χ primitive.

This document is the experimental protocol for the only test that can move the needle on Agent Architectures Problem 1. Controlled stress tests of the engineered process class $\mathcal{P}_{\text{parity}}$ are already complete and do not substitute for it.

---

## 1. What is already prepared (local / controlled)

1. Pure χ primitive — dependency-free, stdlib only, parity-trap self-check GREEN.
2. Four controlled environments (Door, Polarity, Commitment-Gated Recon, Hard Regime-Shift) with adaptive pure-visible baselines defeated. These are explicit stress tests of $\mathcal{P}_{\text{parity}}$ by construction; they do not claim necessity on real agent trajectories.
3. Eight-line inference-only CARM graft (`ReconstructionGate/carm/`) — injects only titrated $r_\chi$ ($\alpha_r=0.20$), safe token, and guidance hint. Never raw χ. Strict no-op when disabled or import fails.
4. Synthetic CARM schedule — four-way ablation (Full / Frozen / No-reveal / Observer) GREEN on the controlled parity-trap schedule.
5. MemHarness insertion mapping — reconstruction hook identified (`envs.step_with_memory` → `maybe_apply_memory_adaptor`). Retrieved pairs available; cleanest insertion point documented in `SURGICAL_PATCH.md`.

## 2. Hardware requirements (currently blocked)

- Multi-GPU node
- vLLM ≈ 0.8.4
- BGE-M3 embedding server (:8001)
- Official HF checkpoints for the base MemHarness agent

None of the above are present in the current sandbox. No official baseline number will be reported until measured on the proper stack.

## 3. Exact experimental protocol (when hardware is available)

### 3.1 Re-confirm pure MemHarness baseline
- Run the official ALFWorld and WebShop evaluation scripts with the published configuration.
- Record success rates. Expected reference numbers (literature): ≈ 85.2 % ALFWorld / ≈ 75.6 % WebShop.
- Any deviation must be documented before proceeding.

### 3.2 Ablation conditions (config-only)
All four conditions must be runnable by changing only a configuration flag; the graft code path is identical.

| Condition          | χ present | Revealing channel | Notes                                      |
|--------------------|-----------|-------------------|--------------------------------------------|
| original           | no        | n/a               | pure MemHarness                            |
| full χ             | yes       | yes ($\alpha_r=0.20$) | titrated $r_\chi$ + safe token + hint |
| frozen χ           | yes (fixed) | yes             | wrong or fixed polarity                    |
| no-reveal          | yes       | disabled          | falls back to pure visible residual        |

### 3.3 Metrics (mandatory)
On the same seeds / same evaluation splits:

- Absolute success rate per condition (ALFWorld, WebShop separately).
- Gap: Full χ − original, Full χ − frozen, Full χ − no-reveal.
- Capacity / compute matched: parameter count, context length, and wall-clock per episode must be reported and comparable.
- Optional but valuable: fraction of trajectories that exhibit an irreversible early commitment whose correct resolution is not recoverable from the visible residual stream alone (diagnostic for membership in something like $\mathcal{P}_{\text{parity}}$).

### 3.4 Stronger baseline comparison (required for any “advance” claim)
In addition to the pure-visible and frozen ablations, compare against at least one existing mechanism that already maintains latent state or irreversible memory (e.g., hierarchical memory with write gates, explicit belief tracker, or source-first reclaim). Capacity-matched. Without this comparison the experiment cannot distinguish χ from “any extra latent bit helps.”

### 3.5 Success / failure criteria
- **Positive signal (necessary but not sufficient for a foundational claim):** Full χ produces a statistically reliable, capacity-matched gain over original *and* over the stronger latent-state / irreversible-memory baseline on at least one of the two benchmarks, and the gain survives the frozen / no-reveal controls.
- **Null result:** Full χ does not outperform the stronger baselines after capacity matching. This is a valid and publishable outcome; it would indicate that the controlled process class does not capture the dominant failure mode of the official benchmarks.
- **No claim of necessity** will be made from a positive signal alone. Necessity requires either (a) a formal argument that a non-trivial fraction of trajectories belong to a process class for which χ is information-theoretically required, or (b) a demonstration that every competitive alternative fails on the same trajectories while χ succeeds.

## 4. Honesty rules (non-negotiable)

- No official baseline number will be reported until it has been measured on the proper stack.
- Controlled evidence (the four environments) remains controlled evidence of behaviour inside $\mathcal{P}_{\text{parity}}$. It is not evidence of necessity in real agent trajectories.
- Any public communication of results must separate “controlled stress of the engineered process class” from “results on official long-horizon benchmarks.”

## 5. Current recommendation

Execute the protocol above as soon as hardware is available. Until then the controlled stress suite (including hard regime-shift and adaptive pure-visible observers) is the strongest evidence that exists for the scoped claim inside $\mathcal{P}_{\text{parity}}$. It does not close the foundational gap.
