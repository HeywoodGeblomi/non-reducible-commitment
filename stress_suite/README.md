# Commitment Stress Suite

Controlled stress tests of the engineered process class $\mathcal{P}_{\text{parity}}$.

> After an odd number of irreversible commitments, any pure function of the visible history is information-theoretically incomplete **inside this class**. Only a non-reducible commitment bit recovers correct behaviour.

These environments are deliberately constructed so that observations remain informationally independent of the hidden polarity after flips. They demonstrate a clean ablation of a known failure mode. They do **not** claim that real long-horizon agent trajectories belong to $\mathcal{P}_{\text{parity}}$ or that $\chi$ is necessary on those trajectories.

Each environment imports **only** `ChiState` from the pure primitive.

## Environments

| # | Name | Structural test |
|---|------|-----------------|
| 1 | Irreversible Door | One-shot irreversible choice; later observations identical across doors |
| 2 | Polarity Tracker | Hidden polarity flips; observations identical across polarities |
| 3 | Commitment-Gated Reconstruction | Drafts valid under only one polarity; ACCEPT/REJECT must track $\chi$ |
| 4 | Hard Regime-Shift | H=80, ~10 flips, discrete non-stationary regimes that remain observationally equivalent across polarities |

Adaptive pure-visible baselines (EMA, Bayes, change-point, regime-aware) are included and are defeated inside the class.

## Run

```bash
python run_suite.py
# or individually:
python env_irreversible_door.py
python env_polarity_tracker.py
python env_commitment_gated_recon.py
python env_hard_regime_shift.py
```

## Expected pattern (all four)

| Method | Performance |
|--------|-------------|
| Reactive / no memory | ~chance |
| Visible-history only | collapses after flips |
| Adaptive pure-visible (EMA / Bayes / RegimeAware) | collapses after flips |
| Full $\chi$ + reveal | high / theoretical ceiling |
| Frozen $\chi$ | collapses or partial |
| $\chi$, reveal disabled | collapses to visible-history |

`is_reducible(visible_history) == False` after an odd number of commits.
