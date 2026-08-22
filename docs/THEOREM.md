# χ Theorem Specification (NRC-THM-001)

**Status:** Phase T + Phase P complete. T1–T5 machine-checked green on main. promote_ready = false (Phase C blocked — no consumer yet). χ is specified, not yet used.

**Scope.** This document states five numbered, machine-checkable claims about the non-reducible commitment bit χ implemented by `ChiState` in this repository. It is a specification, not a Fields Medal theorem. Claims are scoped to the pure primitive and its use as a selector among already-tied alternatives. No physics, no MWI, no consciousness language, no sort policy.

χ is a one-bit (or small-state) dynamic commitment. When used to select one element of a finite set F of already-tied alternatives it must not change membership of F or any ranking of F.

## Claims

**T1 Completeness.**  
ChiState is total: `commit()` always returns χ ∈ {0,1}; `polarity()` always returns ±1; `reveal(α)` always returns a float in [−1, +1]. When a selector is built on top of ChiState, |F|=0 fails closed, |F|=1 returns the sole element, and |F|≥2 returns an element of F.

**T2 Rank-invariance (consumer).**  
χ never mutates membership or ranking of F; any derived pick leaves external ranks unchanged. The primitive itself never receives or writes ranks.

**T3 Determinism.**  
Identical initial `ChiState` + identical sequence of `commit()` and `reveal(α)` calls yield identical (χ, polarity, r_χ, flips, step) trajectory and identical `safe_token()`.

**T4 Binding.**  
After any commit sequence the value of χ (and polarity) is a deterministic function of initial χ and commit-count mod 2; `reveal(α)` is a deterministic function of the committed polarity, prior r_χ and α. No two inconsistent polarity values can be opened for the same commitment history without the oracle `force()`.

**T5 Hiding (operational).**  
After an odd number of commits, `is_reducible` returns False and the parity-trap claim holds. A pure function of F alone (including SHA256(sorted F) or any static hash that omits the dynamic commit+reveal tape / `safe_token`) cannot recover the polarity or serve as a sufficient substitute for the real ChiState selector; such a hash-only implementation must fail the recovery / trap tests that the real primitive passes.

## Proof sketches

- **T1–T4** follow by direct inspection of `ChiState` source and induction on the number of commits (χ is flipped by XOR; reveal is an EMA of polarity; safe_token and observer_features never embed the raw bit).
- **T5** follows from the existing `demonstrate_parity_trap` (claim_holds) together with the definition of `is_reducible`. Any pure function of a visible residual that does not depend on the hidden χ cannot distinguish the two polarities after an odd number of flips; therefore a static hash of F alone cannot pass the same recovery assertions.

## Non-goals

- No Lean / Coq formalization required.
- No Phase C consumer wiring (PrymGyroSort `chi_pick`) until deliberately GO’d.
- No changes to gyro_rank.hpp, PhotonicSort, GeblomiSort, or any sorting policy.
- No S-tier language. Grade target B / B+.

## Acceptance

| ID | Pass condition |
|----|----------------|
| T0 | This file exists with T1–T5 only |
| P1 | Automated tests for T1–T4 green |
| P2 | T5 fails pure hash-on-F; passes commit+reveal tape |
| C0 | Phase C not started; promote_ready remains false |
| X  | No forbidden files touched |

Machine-check: `python -m unittest tests.test_thm -v` (17 tests, OK).

EXTERNAL-or-die remains a separate repository and claim surface.
