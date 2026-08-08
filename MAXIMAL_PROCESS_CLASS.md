# Maximal Process Class for Non-Reducible Commitment

**Heywood Geblomi**  
Formal note · v0.1 · 2026-08-07  
Companion to FORMAL_CLAIM.md and the pure χ primitive.

This note tightens the definition of the process class, states the mutual-information claim rigorously, records a simple sample-complexity observation, and makes the maximality condition explicit. It remains scoped: nothing here claims that real long-horizon agent trajectories belong to the class.

---

## 1. Process class $\mathcal{P}_{\text{parity}}$

A discrete-time decision process belongs to $\mathcal{P}_{\text{parity}}$ if it satisfies all of the following:

1. **Hidden irreversible bit.**  
   There exists a hidden binary state $\chi_t \in \{0,1\}$ that flips only at irreversible commitment times $t \in \mathcal{C}$. Between commitment times $\chi$ is constant.

2. **Parity determines optimal continuation.**  
   After an odd number of flips (i.e., when the parity of $|\mathcal{C} \cap [0,t]|$ is odd), the optimal action (or reconstruction / gating decision) is a non-constant function of the current value of $\chi_t$.

3. **Informational independence of the visible stream (after odd flips).**  
   Let $h_t = (o_{1:t}, a_{<t})$ be the visible residual history and let $\mathcal{F}_t$ be the class of all (possibly adaptive, possibly randomised) functions $f$ that map finite prefixes of $h$ into a decision or estimate. Then, after an odd number of commitments,
   $$
   I\bigl(\chi_t ; f(h_t)\bigr) = 0
   \qquad\text{for every } f \in \mathcal{F}_t.
   $$
   Equivalently, the observation process can be generated so that the conditional law of any finite window of observations is identical under $\chi_t = 0$ and $\chi_t = 1$.

4. **Controlled revealing channel restores information.**  
   There exists a titrated channel
   $$
   r_t = \alpha \cdot s(\chi_t) + (1-\alpha)\, r_{t-1},
   \qquad s(\chi) = +1\text{ if }\chi=1\text{ else }-1,
   $$
   (or any equivalent positive-mutual-information observation of $\chi$) such that
   $$
   I\bigl(\chi_t ; r_t\bigr) > 0
   $$
   for $\alpha \in (0,1]$.

The four controlled environments already shipped (Door, Polarity Tracker, Commitment-Gated Reconstruction, Hard Regime-Shift) are members of $\mathcal{P}_{\text{parity}}$ by construction.

---

## 2. Scoped claim

**Claim (Necessity and sufficiency inside $\mathcal{P}_{\text{parity}}$).**  
Inside $\mathcal{P}_{\text{parity}}$, every pure function of finite visible history is information-theoretically incomplete for selecting the correct future after an odd number of commitments. An explicit dynamic bit $\chi$ together with a controlled revealing channel is necessary and sufficient for completeness.

**Necessity** follows immediately from condition 3: any map that never receives $\chi$ or $r$ has zero mutual information with the parity that determines the optimal continuation.  
**Sufficiency** follows from condition 4 together with the controlled ablations already performed: when the revealing channel is present, near-ceiling performance is recovered; when it is frozen or disabled, performance collapses.

This claim is locked by construction and by the adaptive pure-visible ablations. It is **not** a claim that real agent trajectories belong to $\mathcal{P}_{\text{parity}}$, nor that $\chi$ is necessary outside the class.

---

## 3. Sample-complexity remark (worst-case inside the class)

Consider any estimator that is restricted to functions of the visible residual history alone (i.e., never observes $\chi$ or $r$). Because the two polarities induce identical observation laws after an odd flip, the estimator’s posterior on parity remains uniform. Distinguishing the correct continuation therefore requires, in the worst case, an exponential number of independent trajectories that differ only in the commitment sequence:
$$
\Omega\bigl(2^{|\mathcal{C}|}\bigr)
$$
samples in the worst case inside $\mathcal{P}_{\text{parity}}$.

By contrast, an agent that receives the revealing channel obtains a constant-rate signal of the current polarity; $O(1/\alpha)$ steps of the leaky integrator suffice to recover the sign of $s(\chi)$ with high probability, independent of $|\mathcal{C}|$.

This is a worst-case observation inside the engineered class only. It does not transfer to processes that violate condition 3.

---

## 4. Maximality condition

The claim fails as soon as any of the following is dropped:

- **Drop informational independence (condition 3).**  
  If the observation process retains positive mutual information with $\chi$ after odd flips, then a sufficiently powerful pure-visible (or latent-state) estimator may recover the parity without an explicit commitment bit. This is precisely the direction of the new controlled environment $E^*$: weak residual correlations are allowed, yet long-horizon tracking under realistic noise and regime drift is still required to fail for ordinary latent-state baselines.

- **Drop the irreversible character of the flips.**  
  If the agent can revise or soft-reset the commitment, standard belief tracking regains completeness.

- **Drop the requirement that optimal continuation depends on the current parity.**  
  If the optimal policy is independent of $\chi$ after flips, the bit is superfluous.

Thus $\mathcal{P}_{\text{parity}}$ is maximal with respect to the pure-visible incompleteness claim in the following precise sense: any strictly larger class that relaxes condition 3 admits processes for which some pure (or latent-state) function of the visible stream is already complete.

---

## 5. Status and next formal steps

| Item | Status |
|------|--------|
| Definition of $\mathcal{P}_{\text{parity}}$ | Locked (this note) |
| Mutual-information claim (incl. adaptive $f$) | Locked |
| Sample-complexity remark (worst-case) | Recorded |
| Maximality condition | Explicit |
| Membership of real agent trajectories | **Open** (not claimed) |
| Bounds outside pure observational equivalence | Open (requires $E^*$ or official baselines) |

Immediate formal work that remains zero-hardware:
- Tighten the definition of the function class $\mathcal{F}_t$ (include finite-memory adaptive maps, online learners, etc.).
- State a precise regret or finite-sample recovery rate for the revealing channel.
- Formalise the “escape” condition that $E^*$ must satisfy in order to sit strictly outside $\mathcal{P}_{\text{parity}}$ while still exhibiting a useful separation.

---

**Honesty rule.** This document formalises a scoped theorem-candidate inside an engineered process class. It does not assert that the open problem in long-horizon agent architectures has been solved.
