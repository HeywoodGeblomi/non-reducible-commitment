# χ Primitive — Pure C11

Opaque `ChiState` (incomplete type). Raw χ never appears in public layout.
`chi_export_visible()` / `chi_safe_token()` are the observer surfaces.

## Build

```bash
# Primitive self-check
gcc -O2 -std=c11 -DCHI_PRIMITIVE_DEMO -o chi_primitive chi_primitive.c -lm
./chi_primitive

# Full C stress suite (all three environments)
gcc -O2 -std=c11 -o door_suite env_irreversible_door.c chi_primitive.c -lm
gcc -O2 -std=c11 -o polarity_suite env_polarity_tracker.c chi_primitive.c -lm
gcc -O2 -std=c11 -o recon_suite env_commitment_gated_recon.c chi_primitive.c -lm
./door_suite && ./polarity_suite && ./recon_suite
```

## Memory contract

| API | Copies χ? |
|-----|-----------|
| `ChiVisible` / `chi_export_visible` | **No** |
| `chi_safe_token` | **No** |
| `memcpy` of `ChiState` | **Impossible** (incomplete type) |
| `chi_polarity` / `chi_force` | Privileged (oracle / ablation only) |

## Measured gaps (C) — complete suite

| Environment | Full χ | Visible-history | Gap |
|-------------|--------|-----------------|-----|
| Irreversible Door | +11.00 | −11.00 | +22.00 |
| Polarity Tracker | +20.00 | −1.73 | +21.73 |
| Commitment-Gated Reconstruction | +11.13 | +0.93 | +10.20 |

Frozen / no-reveal collapse in all three. Same structural failure mode across domains.
