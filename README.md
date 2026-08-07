# Non-Reducible Commitment Bit (χ)

A single dynamic bit that stores irreversible information the visible system cannot retain.  
It is recoverable only through a controlled revealing channel.  
After an odd number of transitions, any pure function of the visible history is information-theoretically incomplete.

We extracted χ as a dependency-free primitive and tested it, unchanged, in three minimal environments:

| Environment | Full χ + reveal | Visible-history | Gap |
|-------------|-----------------|-----------------|-----|
| Irreversible Door | +11.0 | –5.8 | +16.8 |
| Polarity Tracker | +20.0 | –0.3 | +20.3 |
| Commitment-Gated Reconstruction | +11.1 | –1.5 | +12.6 |

Same object. Three domains. Same structural collapse when χ is removed; near-perfect recovery when it is restored.

**Technical note (v0.2):** [TECHNICAL_NOTE.md](TECHNICAL_NOTE.md)

These are controlled stress tests. Results on official long-horizon agent benchmarks remain open.

---

## Quick start

```bash
# Primitive self-check
python chi_primitive/chi_primitive.py

# Full stress suite
cd stress_suite && python run_suite.py
```

## General finder (any system)

```bash
python dcl/find_chi.py              # full self-check (BANGER)
python dcl/find_chi.py --one-word   # e.g. RUPTURE
```

```python
from find_chi import log_chi, Observation
word = log_chi(stream)   # CLEAR | SHADOW | RAPTURE | RUPTURE
# never emits raw chi — safe for logs
```

Engineering brief: [ENGINEERING_BRIEF.txt](ENGINEERING_BRIEF.txt)

Zero-lift axiom: true-zero is absorbing under × and ÷; only ± lifts a system out.
χ is the shadow of that lift — not the distance scalar, not photon cargo.

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
├── ENGINEERING_BRIEF.txt
├── RELEASE_NOTES.md
├── chi_primitive/
│   ├── chi_primitive.py
│   └── README.md
├── dcl/
│   └── find_chi.py          # general finder + one-word API
└── stress_suite/
    ├── env_irreversible_door.py
    ├── env_polarity_tracker.py
    ├── env_commitment_gated_recon.py
    ├── run_suite.py
    └── README.md
```

## Related work

Applications of the same primitive (residual diagnostics, reconstructive memory agents) live in the [reconstruction-gate](https://github.com/HeywoodGeblomi/reconstruction-gate) repository. This repository isolates the general object.

## License

MIT
