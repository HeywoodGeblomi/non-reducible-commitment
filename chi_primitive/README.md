# Non-Reducible Commitment Bit (χ)

A single dynamic bit that stores irreversible information the visible system is forbidden to retain.  
Recoverable only through a controlled revealing channel.  
Any pure function of the visible history is information-theoretically incomplete after an odd number of transitions.

**Dependency-free. Stdlib only. Re-implementable in <30 minutes.**

## Contract

```python
from chi_primitive import ChiState, is_reducible, demonstrate_parity_trap

st = ChiState()              # χ ∈ {0,1}
st.commit()                  # irreversible flip χ ← χ ⊕ 1
r  = st.reveal(alpha=0.20)   # titrated partial observation of χ
p  = st.polarity()           # +1 if χ=1 else −1
token = st.safe_token()      # never contains raw χ

# Parity-trap probe
assert demonstrate_parity_trap()["claim_holds"]
```

## What this is

The pure commitment object. No residual signal, no dual-signal, no verdict logic, no agent policy.

Those live in the surrounding systems:

| System | Role of χ |
|--------|-----------|
| Reconstruction Gate | χ + dual signal → ACCEPT / REWRITE / REJECT |
| CARM | χ grafted onto reconstructive memory agents |
| Residual monitors | χ drives polarity / rigidity of the diagnostic process |
| Toy POMDPs (forthcoming) | χ stores irreversible door / goal / polarity choices |

## What this is not

- Not a full agent memory system  
- Not a residual diagnostic  
- Not dependent on MemHarness, Reconstruction Gate, or any external package  

## Reproducibility

```bash
python chi_primitive.py
```

Expected: parity-trap demonstration passes (`claim_holds: True`).

## Lineage

Dynamic Commitment Layer → Reconstruction Gate → CARM → **this primitive** (extracted for generality).
