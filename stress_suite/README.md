# Commitment Stress Suite

Controlled stress tests related to the engineered process class $\mathcal{P}_{\text{parity}}$ and its immediate extensions.

These environments demonstrate clean ablations of known failure modes under irreversible commitments. They do **not** claim that real long-horizon agent trajectories belong to $\mathcal{P}_{\text{parity}}$ or that $\chi$ is necessary on those trajectories.

Each environment imports **only** `ChiState` from the pure primitive.

## Environments inside pure observational equivalence

| # | Name | Structural test |
|---|------|-----------------|
| 1 | Irreversible Door | One-shot irreversible choice; later observations identical across doors |
| 2 | Polarity Tracker | Hidden polarity flips; observations identical across polarities |
| 3 | Commitment-Gated Reconstruction | Drafts valid under only one polarity; ACCEPT/REJECT must track $\chi$ |
| 4 | Hard Regime-Shift | H=80, ~10 flips, discrete non-stationary regimes that remain observationally equivalent across polarities |

Adaptive pure-visible baselines (EMA, Bayes, change-point, regime-aware) are defeated inside this class.

## Environments that escape pure observational equivalence

| # | Name | Structural test |
|---|------|-----------------|
| 5 | E* (Escape) | Weak residual (SNR ≈ 0.22) + independent bias drift; Bayesian / FixedBuffer / EMA still fail; Full $\chi$ recovers ceiling |
| 6 | E** (Still-harder) | Moderate residual (SNR ≈ 0.40) + independent corr-sign flips + amplitude modulation + bias RW/jumps + residual-regime drift; stronger latents (Bayesian+process-noise, Hierarchical buffer, Multi-scale EMA, Kalman-style) still fail; Full $\chi$ recovers theoretical ceiling (+120) |

Both E* and E** remain controlled stress tests. They do not claim membership of real agent trajectories in $\mathcal{P}_{\text{parity}}$.

## Run

```bash
python run_suite.py                              # original four (inside pure observational equivalence)
python env_escape_observational_equivalence.py   # E*
python env_E_double_star.py                      # E**
```

## Expected pattern

Inside pure observational equivalence: Full $\chi$ near ceiling; pure-visible and adaptive pure-visible collapse.

On E* / E**: Full $\chi$ near ceiling; latent-state and hierarchical baselines remain near zero (gaps ~85–120 points). Residual carries real mutual information, yet ordinary trackers lose the parity under non-stationarity + irreversible flips.

`is_reducible` helper remains False after odd commits on the parity-trap schedule.
