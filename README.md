# Non-Reducible Commitment Bit (χ)

A single dynamic bit that stores irreversible information the visible system cannot retain.  
It is recoverable only through a controlled revealing channel.  
After an odd number of transitions, any pure function of the visible history is information-theoretically incomplete **inside a deliberately constructed process class**.

We extracted χ as a dependency-free primitive and tested it in controlled environments.

| Environment | Full χ + reveal | Stronger baselines | Gap (approx.) |
|-------------|-----------------|--------------------|---------------|
| Irreversible Door | +11.0 | collapse | +16–17 |
| Polarity Tracker | +20.0 | ~0 | +20 |
| Commitment-Gated Reconstruction | +11.1 | collapse | +12–15 |
| Hard Regime-Shift (H=80) | +80.0 | ~0 | ~80 |
| E* (escapes pure obs. equivalence) | +90.0 | Bayesian / FixedBuffer ~3–5 | ~85 |
| E** (still-harder) | +120.0 | Hierarchical / Multi-scale / Kalman / Bayesian+PN ~0–3 | ~117–120 |

**These are controlled stress tests.**  
They demonstrate clean ablations of known failure modes under irreversible commitments. They do **not** constitute evidence that real long-horizon agent trajectories belong to $\mathcal{P}_{\text{parity}}$, nor that χ is necessary or superior to existing latent-state / irreversible-memory mechanisms on those trajectories. Foundational advance on the open problem remains gated on official baselines or further work outside pure construction.

**Technical note (v0.2):** [TECHNICAL_NOTE.md](TECHNICAL_NOTE.md)  
**Formal claim (v0.1):** [FORMAL_CLAIM.md](FORMAL_CLAIM.md)  
**χ Theorem specification (NRC-THM-001):** [docs/THEOREM.md](docs/THEOREM.md) — T1–T5 (completeness, rank-invariance, determinism, binding, operational hiding). Machine-checked in `tests/test_thm.py`. promote_ready=false until Phase C consumer.  
**Maximal process class:** [MAXIMAL_PROCESS_CLASS.md](MAXIMAL_PROCESS_CLASS.md) — definition, MI claim, maximality condition  
**Path to baseline:** [PATH_TO_BASELINE.md](PATH_TO_BASELINE.md) — complete protocol for official ALFWorld / WebShop (capacity-matched, stronger baselines required)

Official long-horizon agent baselines remain the open gate.

---

## Quick start

```bash
# Primitive self-check
python chi_primitive/chi_primitive.py

# χ Theorem machine-check (NRC-THM-001 T1–T5)
python -m unittest tests.test_thm -v

# Full stress suite (inside pure observational equivalence)
cd stress_suite && python run_suite.py

# E* / E** (escape pure observational equivalence)
python env_escape_observational_equivalence.py
python env_E_double_star.py
```

## Contract

```python
from chi_primitive import ChiState, demonstrate_parity_trap

st = ChiState()              # χ ∈ {0,1}
st.commit()                  # irreversible flip
r  = st.reveal(alpha=0.20)   # titrated revealing channel
p  = st.polarity()           # +1 / −1
token = st.safe_token()      # never contains raw χ

assert demonstrate_parity_trap()["claim_holds"]
```

Dependency-free. Stdlib only. Re-implementable in <30 minutes.

## Layout

```
non-reducible-commitment/
├── README.md
├── LICENSE
├── TECHNICAL_NOTE.md
├── FORMAL_CLAIM.md
├── MAXIMAL_PROCESS_CLASS.md
├── PATH_TO_BASELINE.md
├── RELEASE_NOTES.md
├── docs/
│   └── THEOREM.md          # NRC-THM-001 T1–T5 specification
├── tests/
│   └── test_thm.py         # machine-check for T1–T5
├── chi_primitive/
│   ├── chi_primitive.py
│   └── README.md
└── stress_suite/
    ├── env_irreversible_door.py
    ├── env_polarity_tracker.py
    ├── env_commitment_gated_recon.py
    ├── env_hard_regime_shift.py
    ├── env_escape_observational_equivalence.py
    ├── env_E_double_star.py
    ├── run_suite.py
    └── README.md
```

## Related work

Companion applications of this primitive (residual diagnostics, reconstructive memory) are private. This repository isolates the general object. Companion is private.

## License

**Dual licensed.**

- Non-commercial / research / evaluation / non-production → [AGPLv3](LICENSE-AGPL)
- Commercial / production / embedding / SaaS / redistribution as product → requires a [paid proprietary Commercial License](LICENSE-COMMERCIAL)

See [LICENSE](LICENSE) for the dual statement and [COMMERCIAL.md](COMMERCIAL.md) for how to request a grant.

Until a commercial grant is issued in writing, AGPLv3 governs all use.
