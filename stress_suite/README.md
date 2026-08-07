# Commitment Stress Suite

Three minimal environments. Same primitive. Same information gap.

Live numbers (`python run_suite.py`, 80 episodes):

| Environment | Full χ + reveal | Visible-history | Gap |
|-------------|-----------------|-----------------|-----|
| Irreversible Door | +11.0 | +0.6 | +10.4 |
| Polarity Tracker | +20.0 | −0.3 | +20.3 |
| Commitment-Gated Reconstruction | +11.1 | −1.5 | +12.6 |

Frozen-χ ablations collapse on all three. Free choice at door-selection; χ is frozen only *after* the irreversible act.

```bash
python run_suite.py
```

`is_reducible == False` after odd commits.
