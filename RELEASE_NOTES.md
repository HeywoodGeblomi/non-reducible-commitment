# Release Notes — Non-Reducible Commitment Bit

## v0.2.1 (2026-08-07)

Surgical empirical tightness pass:

- Irreversible Door: free choice at t=0 for all agents; χ frozen only *after* the act
- Frozen χ=0 / χ=1 now collapse (was incorrectly matching Full)
- `safe_token()` uses `peek()` — no integrator side-effect on read
- README + suite tables locked to live `run_suite.py` numbers

Live gaps: Door +10.4 · Polarity +20.3 · Recon +12.6

## v0.2 (2026-08-07)

- Pure χ primitive extracted (`ChiState` + revealing channel)
- Commitment Stress Suite: three environments with decisive separations
- Technical note v0.2 with §7 “The Primitive Across Domains”
- Dependency-free, stdlib only

## Status

Formal non-reducibility claim and controlled stress-test evidence locked.  
Official long-horizon agent benchmark confirmation remains open.
