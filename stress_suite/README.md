# Commitment Stress Suite

Controlled stress tests related to the engineered process class $\mathcal{P}_{\text{parity}}$ and its immediate extension.

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

## Environment that escapes pure observational equivalence

| # | Name | Structural test |
|---|------|-----------------|
| 5 | E* (Escape) | Weak residual correlations with polarity (SNR ≈ 0.22) + independent bias drift; latent-state Bayesian filter and fixed residual buffer still fail; Full $\chi$ recovers ceiling |

This is still a controlled stress test. It does not claim membership of real agent trajectories in $\mathcal{P}_{\text{parity}}$.

## Run

```bash
python run_suite.py          # original four (inside pure observational equivalence)
python env_escape_observational_equivalence.py   # E*
```

## Expected pattern

Inside pure observational equivalence: Full $\chi$ near ceiling; pure-visible and adaptive pure-visible collapse.

On E*: Full $\chi$ near ceiling; Bayesian filter / FixedBuffer latent / EMA remain low (gaps ~85 points in the reported run). Residual carries real mutual information, yet ordinary latent-state trackers lose the parity under low SNR + bias drift + multiple irreversible flips.

`is_reducible` helper remains False after odd commits on the parity-trap schedule.
