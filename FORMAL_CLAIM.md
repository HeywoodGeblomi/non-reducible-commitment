# Formal Claim: Non-Reducible Commitment under Observational Ambiguity

**Heywood Geblomi**  
Mathematical core for Agent Architectures — Problem 1  
Version 0.1 · 2026-08-07  
Companion to TECHNICAL_NOTE.md v0.2 and the pure χ primitive.

---

## 0. Scope and honesty

This note states a scoped theorem-candidate. It does **not** claim that every long-horizon agent requires a hidden commitment variable. It claims that there exists a non-empty process class $\mathcal{P}_{\text{parity}}$ for which:

1. any pure function of the finite visible residual history is information-theoretically incomplete, and
2. a single dynamic bit $\chi$ together with a controlled revealing channel restores completeness for the selection among observationally consistent futures.

**Critical limitation.** The process class is engineered so that observations are informationally independent of the hidden polarity after commitment flips. Under that construction the incompleteness of pure-visible methods (including adaptive ones) follows by information theory, and $\chi$ succeeds because it is an explicit external copy of the hidden state. This is a clean ablation of a known failure mode. It is **not** evidence that real long-horizon agent trajectories belong to $\mathcal{P}_{\text{parity}}$ in a way that makes this primitive necessary, nor that it outperforms existing latent-state or irreversible-memory mechanisms on those trajectories.

All quantitative separation remains synthetic or controlled stress-test. Official long-horizon agent baselines are open. Foundational advance on the open problem remains gated on those baselines (or on a qualitatively harder controlled stress that escapes pure observational equivalence).

---

## 1. Process class $\mathcal{P}_{\text{parity}}$

Fix a discrete-time decision process with:

- latent state $s_t \in \mathcal{S}$,
- observation $o_t \in \mathcal{O}$,
- action $a_t \in \mathcal{A}$,
- visible residual history $h_t = (o_{\leq t}, a_{<t}, m_t)$ where $m_t$ is any finite memory or reconstructive draft derived solely from past observations and actions.

A process belongs to $\mathcal{P}_{\text{parity}}$ when it admits a **parity-trap schedule**:

There exist times $0 \le t_1 < t_2 < \dots < t_k$ and a hidden bit sequence $\chi_t \in \{0,1\}$ such that:

- $\chi$ flips exactly at the $t_i$ (i.e., $\chi_{t_i} = \chi_{t_i-1} \oplus 1$),
- after an odd number of flips the optimal continuation policy (or the correct reconstruction / polarity / door) is the opposite of the pre-flip optimum,
- yet there exists an observational equivalence: the distribution of future observations (and therefore of any pure function of finite windows of $h$) can be made identical before and after the odd flip.

Formally, there exist two regimes $R_+$ and $R_-$ that are observationally equivalent under every finite window of $h$, yet the optimal action (or correct memory gate) differs:

$$
\mathbb{P}(o_{t+\cdot} \mid h_t, R_+) = \mathbb{P}(o_{t+\cdot} \mid h_t, R_-)
\quad\text{while}\quad
\pi^*(h_t, R_+) \ne \pi^*(h_t, R_-).
$$

The three minimal environments plus the hard regime-shift variant are members of $\mathcal{P}_{\text{parity}}$.

---

## 2. Incompleteness of pure visible maps

**Claim 1 (Non-reducibility).**  
Let $\Phi$ be any map from finite windows of the visible residual history $h$ into completions, reconstructions, polarity estimates, or actions.  
Under any process in $\mathcal{P}_{\text{parity}}$, after an odd number of commitment flips there exist histories for which

$$
\Phi(h_t) \ne \text{correct continuation / polarity / gate}.
$$

In other words, no pure function of the visible residual stream recovers the information that selects among the observationally consistent futures.

**Sketch.**  
By construction of the parity trap the two regimes produce identical finite visible windows yet require opposite optimal behaviour. Any $\Phi$ that is a function of those windows alone must output the same value on both regimes and therefore errs on at least one of them. The error is permanent relative to the visible stream; it cannot be erased by longer memory of $h$ alone.

This is the precise sense in which standard belief-state / POMDP / RAG / reconstructive-memory tokens are incomplete for $\mathcal{P}_{\text{parity}}$: they remain pure (or effectively pure) functions of the visible residual.

---

## 3. What $\chi$ supplies

Introduce a dynamic bit $\chi_t \in \{0,1\}$ that is updated only by irreversible commitment acts

$$
\chi \leftarrow \chi \oplus 1
$$

and is never written into the ordinary residual stream. Attach a controlled revealing channel (leaky integrator)

$$
r_\chi \leftarrow (1-\alpha)\, r_\chi + \alpha\, s(\chi), \qquad s(\chi) = +1\text{ if }\chi=1\text{ else }-1,
$$

with small $\alpha$ (empirically $\alpha \approx 0.20$).

The pair $(\chi, r_\chi)$ has three properties:

1. **Irreversibility.** After an odd number of commits the polarity has flipped and cannot be recovered from any pure function of $h$.
2. **Titrated recoverability.** The scalar $r_\chi$ asymptotically tracks the correct polarity; an agent that is allowed to read $r_\chi$ (but never raw $\chi$) recovers the selection bit.
3. **Non-pollution.** The ordinary context and residual stream never contain the integer $\chi$; only a safe token derived from $r_\chi$ may be injected.

**Claim 2 (Sufficiency for the process class).**  
On every tested member of $\mathcal{P}_{\text{parity}}$ the agent that receives the titrated channel $r_\chi$ (or the safe token) restores near-optimal behaviour, while every pure visible baseline collapses. The measured gaps on the controlled environments remain large after adaptive pure-visible observers are included.

---

## 4. Relation to existing primitives

| Standard object              | Relation to $\mathcal{P}_{\text{parity}}$                          |
|-----------------------------|---------------------------------------------------------------------|
| Belief state / POMDP filter | Explodes or remains incomplete once observational equivalence holds |
| Reconstructive memory draft | Necessary but not sufficient; the draft itself can be valid under both polarities |
| RAG / vector memory tokens  | Pure functions of visible history; fall under Claim 1               |
| Hidden state + EMA          | Can approximate $r_\chi$ only if the hidden state is allowed to carry the irreversible bit; most practical implementations do not enforce non-reducibility |
| Classical commitment schemes| Cryptographic; different security model and different interface     |

$\chi$ is therefore not a re-packaging: it is the minimal dynamic object that is simultaneously irreversible, recoverable only through a controlled channel, and deliberately excluded from the ordinary residual stream *inside the engineered class*.

---

## 5. Adaptive observers (controlled)

The stress suite includes stronger pure-visible adaptive baselines (EMA, Bayes/frequency, change-point, regime-aware). All remain near chance or worse after odd flips. Full $\chi$ + reveal retains the theoretical maximum (or near-maximum). The gaps survive the stronger observers *inside $\mathcal{P}_{\text{parity}}$*.

## 6. Hard regime-shift variant (controlled)

A fourth environment stresses the claim under longer horizon (H=80), multiple flips, and discrete non-stationary observation regimes that remain observationally equivalent across polarities. Full $\chi$ + reveal reaches the theoretical ceiling. Every pure-visible method (including a regime-aware adaptive baseline) collapses. This tightens the controlled demonstration; it does not escape the engineered process class.

## 7. Open gates (remaining)

- Official MemHarness ALFWorld / WebShop baseline (hardware-gated).
- Still-stronger meta-learners or agents allowed privileged side information about the observation process.
- Finite-sample / regret analysis of the revealing channel.
- Extension of the process class beyond pure observational equivalence (the harder controlled stress that would actually move the needle).

Until those gates are closed the claim remains a theorem-candidate with decisive controlled evidence inside $\mathcal{P}_{\text{parity}}$, not a finished empirical demonstration on large-scale agents and not a foundational advance on the open problem.

---

## 8. Artifacts

| Path | Role |
|------|------|
| `chi_primitive/chi_primitive.py` | Pure implementation (stdlib only) |
| `stress_suite/` | Four environments + adaptive observers |
| `TECHNICAL_NOTE.md` | Broader research narrative (v0.2) |
| `PATH_TO_BASELINE.md` | Complete protocol for the official baseline experiment |
| This file | Mathematical core |

Self-check:

```bash
python chi_primitive/chi_primitive.py
# claim_holds must be True
cd stress_suite && python run_suite.py
```

---

**Status.** Formal process class $\mathcal{P}_{\text{parity}}$ and non-reducibility claim inside it locked at v0.1 (by construction + stronger controlled ablations). Adaptive pure-visible observers and hard regime-shift variant defeated *inside that class*. Pure $\chi$ primitive remains minimal and clean. **Foundational advance on the open problem in agent architectures is not yet achieved**; it remains gated on official baselines or a qualitatively harder controlled stress that escapes pure observational equivalence.
