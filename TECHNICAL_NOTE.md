# Making Reconstructive Memory Permanent:  
Non-Reducible Commitment for Long-Horizon Agents

**Heywood Geblomi**  
Technical Note — CARM v0.2  
August 2026

---

## Abstract

We present a minimal hybrid layer (CARM) that attaches a dynamic hidden commitment variable χ to reconstructive memory agents, and extract the same object as a dependency-free primitive. On a controlled parity-trap schedule the construction produces a clean four-way separation: full CARM recovers correct post-flip behaviour (100 % Phase-C success), a wrong-frozen commitment collapses (0 %), disabling the revealing channel halves success (50 %), and an observer limited to visible history recovers nothing (0 %). Placed unchanged into three minimal stress environments (irreversible choice, polarity tracking, commitment-gated reconstruction), the primitive yields the same near-perfect vs collapse pattern, with gaps of +12 to +20 return points against visible-history baselines. The entire live-code change required to graft the layer onto a MemHarness-style agent is an eight-line, fully reversible block that injects only a titrated revealing channel r_χ (α_r=0.20), a commitment token, and a guidance hint — never raw χ.

All quantitative separation reported here is synthetic or controlled stress-test. Confirmation on the official MemHarness ALFWorld / WebShop stack, and on hard regime-shift variants, remains the open empirical gate.

---

## 1. Problem

Reconstructive memory (Wu et al., 2026) established that retrieved experience must be critiqued and rewritten against the current state before it is allowed to influence action. That result is necessary. Under observational ambiguity it is not always sufficient.

There exist decision processes in which:

1. multiple futures remain consistent with any finite window of visible observations,
2. the information required to select among those futures is not retained in the visible residual or memory history, and
3. an irreversible early commitment must constrain later reconstruction.

In such regimes any pure function of the visible trace is information-theoretically incomplete relative to the process class defined below. A dynamic hidden commitment variable becomes necessary under that definition.

---

## 2. Non-Reducible Commitment

Define a process class in which a hidden bit χ ∈ {0,1} flips under a parity-trap schedule: after an odd number of flips, polarity reverses while the visible residual stream is observationally identical to the pre-flip regime. Any pure function of finite visible history cannot recover the correct polarity. The information gap is permanent relative to the visible residual history.

The Reconstruction Gate and CARM supply that variable together with a controlled revealing channel r_χ (leaky integrator, α_r ≈ 0.20) that titrates observation of χ without ever exposing the raw bit to ordinary context.

---

## 3–6. CARM Mechanism, Synthetic Separation, Inference-Only Graft

(Full detail in companion reconstruction-gate repository. Summary: four-way ablation GREEN — Full 100%, Frozen 0%, No-reveal 50%, Observer 0%. Eight-line reversible graft injects only titrated r_χ + token + hint.)

---

## 7. The Primitive Across Domains

The non-reducible commitment bit is not an artifact of residual diagnostics or of MemHarness. It is a general mechanism for irreversible selection among observationally consistent futures. To test that claim, χ was extracted as a dependency-free primitive (`ChiState`) and placed, unchanged, into three minimal stress environments.

**Irreversible Door.**  
At step 0 the agent chooses Left or Right. Thereafter all observations are drawn from the same distribution regardless of the choice, yet the optimal later actions are determined by the initial door. Full χ + reveal recovers the door perfectly (avg return +11.0); visible-history collapses (−5.8). Gap +16.8.

**Polarity Tracker.**  
A hidden polarity flips at random intervals while observations remain identically distributed across polarities. Correct action tracks the true polarity. Full χ + reveal achieves the theoretical maximum (+20.0); visible-history stays near chance (−0.3). Gap +20.3.

**Commitment-Gated Reconstruction.**  
The agent receives draft “memories” that are valid under only one polarity. After an irreversible flip the same draft must be rejected. Full χ + reveal correctly gates ACCEPT/REJECT (+11.1); visible-history and always-accept baselines fail (−1.5 / −4.3). Gap +12.6.

| Environment | Full χ + reveal | Visible-history | Gap |
|-------------|-----------------|-----------------|-----|
| Irreversible Door | +11.0 | –5.8 | +16.8 |
| Polarity Tracker | +20.0 | –0.3 | +20.3 |
| Commitment-Gated Reconstruction | +11.1 | –1.5 | +12.6 |

Across all three settings the same structural failure appears once the commitment bit is removed: after an odd number of transitions, any pure function of the visible history becomes incomplete and performance collapses. Restoring χ together with the revealing channel recovers near-perfect behaviour. This is evidence that χ + revealing channel functions as a domain-agnostic primitive.

These are controlled stress tests, not large-scale agent results. They demonstrate structural necessity under observational ambiguity; they do not yet measure practical gain on official long-horizon benchmarks.

---

## 8. What is Locked vs. Pending

| Claim | Status |
|-------|--------|
| Non-reducibility of χ under the parity-trap process class | Locked (formal + synthetic) |
| Revealing channel recovers χ at α_r≈0.20 | Locked |
| Four-way ablation separation on synthetic schedule | Locked |
| Pure χ primitive (dependency-free) | Locked |
| Commitment Stress Suite (3 environments, decisive gaps) | Locked |
| Pure MemHarness baseline (ALFWorld / WebShop) | **Pending (real hardware)** |
| Hard-variant agent gap | **Pending** |
| Stronger adaptive observers | **Pending** |

---

## 9. Limitations (read first)

- **All quantitative separation reported in this note is synthetic or controlled stress-test.** No results have yet been obtained on the official MemHarness ALFWorld or WebShop evaluation stack.
- The non-reducibility argument is scoped to the process class defined by the parity-trap construction. It does **not** claim that every reconstructive-memory problem requires a hidden commitment variable.
- The three stress-suite environments are minimal by design. They demonstrate structural necessity under observational ambiguity; they are not substitutes for large-scale agent evaluation.
- No sample-complexity, regret, or finite-sample analysis is provided.

These limitations are the open gate. The note is a research artifact that isolates a formal claim, a measurable synthetic separation, and a domain-agnostic primitive; it is not a finished empirical demonstration on agent benchmarks.

---

## 10. Artifacts and Reproducibility

**Commitment Stress Suite** (results in §7):

```bash
cd stress_suite && python run_suite.py
```

Expected: decisive gaps in all three environments; `is_reducible == False` after odd commits.

**Primitive self-check:**

```bash
python chi_primitive/chi_primitive.py
```

| Path | Role |
|------|------|
| `TECHNICAL_NOTE.md` | This note |
| `chi_primitive/chi_primitive.py` | Pure Non-Reducible Commitment Bit |
| `stress_suite/` | Three-environment stress suite + runner |
| `README.md` | Public summary + quick start |

Applications (Reconstruction Gate, CARM) live in the companion [reconstruction-gate](https://github.com/HeywoodGeblomi/reconstruction-gate) repository.

---

## 11. Conclusion

Under observational ambiguity, some reconstructive decision processes are information-theoretically incomplete without a dynamic hidden variable. The same primitive, extracted and placed unchanged into three distinct stress environments, produces the identical near-perfect vs collapse separation. Synthetic and controlled results establish both the predicted information gap and a domain-agnostic mechanism that closes it. The remaining empirical gate is confirmation on real agent baselines and hard regime-shift variants.

**Status:** Research-grade technical note v0.2. Formal claim, pure primitive, and three-environment stress suite locked. Real-agent baseline and stronger observer tests pending.
