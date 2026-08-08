/*
 * NON-REDUCIBLE COMMITMENT BIT (chi_primitive.h)
 * Pure C port of the locked Python primitive.
 *
 * Memory contract (deep-copy harden):
 *   - ChiState is an incomplete type. Clients never see χ.
 *   - memcpy / assignment of ChiState is impossible from outside this TU.
 *   - chi_export_visible() copies only observer-safe fields (no χ).
 *   - chi_safe_token() never embeds raw χ.
 *
 * Contract:
 *   ChiState *st = chi_create();
 *   chi_commit(st);
 *   r = chi_reveal(st, alpha);
 *   p = chi_polarity(st);          // privileged (oracle / ablation)
 *   chi_export_visible(st, &vis);  // safe snapshot
 *   chi_destroy(st);
 */

#ifndef CHI_PRIMITIVE_H
#define CHI_PRIMITIVE_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Incomplete type — layout private to chi_primitive.c */
typedef struct ChiState ChiState;

/* Observer-safe snapshot. Safe to memcpy. Does NOT contain χ. */
typedef struct {
    double r_chi;
    int    flips;
    int    step;
} ChiVisible;

/* Lifecycle */
ChiState *chi_create(void);
void      chi_destroy(ChiState *st);
void      chi_init(ChiState *st);   /* reset existing handle to χ=1 */

/* Irreversible commitment: χ ← χ ⊕ 1. Returns new χ (privileged). */
int chi_commit(ChiState *st);

/* Ablation: freeze χ without counting a flip. */
void chi_force(ChiState *st, int chi);

/* Polarity s(χ). Privileged — oracle / full-χ agent only. */
double chi_polarity(const ChiState *st);

/* Revealing channel: rχ ← (1−α)rχ + α·s(χ). Returns updated rχ. */
double chi_reveal(ChiState *st, double alpha);

/* Read rχ without updating. */
double chi_peek(const ChiState *st);

/* Export observer-safe fields only. Never copies χ. */
void chi_export_visible(const ChiState *st, ChiVisible *out);

/*
 * Machine-readable token. Never includes raw χ.
 * Returns buf, or NULL if buflen too small / args invalid.
 */
char *chi_safe_token(ChiState *st, double alpha, int include_r,
                     char *buf, size_t buflen);

/* 1 iff flip count is even. */
int chi_is_reducible(const ChiState *st);

/* Parity-trap self-check. Returns 1 if claim holds. */
int chi_demonstrate_parity_trap(void);

#ifdef __cplusplus
}
#endif

#endif /* CHI_PRIMITIVE_H */
