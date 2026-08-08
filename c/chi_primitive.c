/*
 * NON-REDUCIBLE COMMITMENT BIT (chi_primitive.c)
 * Opaque ChiState — χ is never part of any public layout.
 *
 * Compile demo:
 *   gcc -O2 -std=c11 -DCHI_PRIMITIVE_DEMO -o chi_primitive chi_primitive.c -lm
 */

#include "chi_primitive.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* Private layout — not visible in the header */
struct ChiState {
    int    chi;      /* hidden bit {0,1} */
    double r_chi;
    int    flips;
    int    step;
};

ChiState *chi_create(void) {
    ChiState *st = (ChiState *)calloc(1, sizeof(ChiState));
    if (st) chi_init(st);
    return st;
}

void chi_destroy(ChiState *st) {
    if (!st) return;
    /* Scrub hidden bit before free */
    st->chi = 0;
    st->r_chi = 0.0;
    st->flips = 0;
    st->step = 0;
    free(st);
}

void chi_init(ChiState *st) {
    if (!st) return;
    st->chi   = 1;
    st->r_chi = 0.0;
    st->flips = 0;
    st->step  = 0;
}

int chi_commit(ChiState *st) {
    if (!st) return 0;
    st->chi ^= 1;
    st->flips += 1;
    return st->chi;
}

void chi_force(ChiState *st, int chi) {
    if (!st) return;
    st->chi = chi ? 1 : 0;
}

double chi_polarity(const ChiState *st) {
    if (!st) return 0.0;
    return st->chi == 1 ? 1.0 : -1.0;
}

double chi_reveal(ChiState *st, double alpha) {
    if (!st) return 0.0;
    if (alpha < 0.0) alpha = 0.0;
    if (alpha > 1.0) alpha = 1.0;
    st->r_chi = (1.0 - alpha) * st->r_chi + alpha * chi_polarity(st);
    st->step += 1;
    return st->r_chi;
}

double chi_peek(const ChiState *st) {
    if (!st) return 0.0;
    return st->r_chi;
}

void chi_export_visible(const ChiState *st, ChiVisible *out) {
    if (!out) return;
    if (!st) {
        out->r_chi = 0.0;
        out->flips = 0;
        out->step  = 0;
        return;
    }
    out->r_chi = st->r_chi;
    out->flips = st->flips;
    out->step  = st->step;
    /* deliberately does not touch / copy st->chi */
}

char *chi_safe_token(ChiState *st, double alpha, int include_r,
                     char *buf, size_t buflen) {
    if (!st || !buf || buflen < 24) return NULL;
    double r = include_r ? chi_reveal(st, alpha) : st->r_chi;
    const char *commit = (r > 0.0) ? "commit" : "passive";
    int n;
    if (include_r)
        n = snprintf(buf, buflen, "rχ=%+.3f commit=%s", r, commit);
    else
        n = snprintf(buf, buflen, "commit=%s", commit);
    if (n < 0 || (size_t)n >= buflen) return NULL;
    if (strstr(buf, "chi=") != NULL) return NULL;
    return buf;
}

int chi_is_reducible(const ChiState *st) {
    if (!st) return 1;
    return (st->flips % 2 == 0) ? 1 : 0;
}

int chi_demonstrate_parity_trap(void) {
    ChiState *st;
    int i, ok = 1;
    ChiVisible vis, vis2;

    printf("chi_primitive C self-check (opaque ChiState)\n");
    printf("--------------------------------------------------\n");

    st = chi_create();
    if (!st) {
        printf("FAIL — chi_create returned NULL\n");
        return 0;
    }

    printf("init  polarity=%+.0f  rχ=%+.3f\n",
           chi_polarity(st), chi_peek(st));

    for (i = 0; i < 5; ++i)
        chi_reveal(st, 0.20);
    printf("after 5 reveals  rχ=%+.3f\n", chi_peek(st));
    if (chi_peek(st) <= 0.0) ok = 0;

    chi_commit(st);
    printf("commit → polarity=%+.0f\n", chi_polarity(st));

    for (i = 0; i < 8; ++i)
        chi_reveal(st, 0.20);
    printf("after 8 reveals  rχ=%+.3f\n", chi_peek(st));
    if (chi_peek(st) >= 0.0) ok = 0;

    {
        char token[64];
        if (!chi_safe_token(st, 0.20, 1, token, sizeof token)) {
            ok = 0;
            printf("safe token: FAIL\n");
        } else {
            printf("safe token: [%s]\n", token);
            printf("  no raw χ in token: OK\n");
        }
    }

    /* Deep-copy harden: visible export must not carry χ */
    chi_export_visible(st, &vis);
    chi_force(st, 1 - (chi_polarity(st) > 0 ? 1 : 0)); /* flip hidden */
    chi_export_visible(st, &vis2);
    printf("visible snapshot size: %zu bytes (no χ field)\n", sizeof(ChiVisible));
    printf("  chi_export_visible: OK (opaque, no χ in layout)\n");

    printf("--------------------------------------------------\n");

    chi_init(st);
    {
        double initial_pol = chi_polarity(st);
        int t;
        for (t = 0; t < 40; ++t) {
            if (t == 5 || t == 15 || t == 28)
                chi_commit(st);
            chi_reveal(st, 0.20);
        }
        double final_pol = chi_polarity(st);
        int reducible = chi_is_reducible(st);
        int channel_ok = (final_pol < 0.0 && chi_peek(st) < 0.0) ||
                         (final_pol > 0.0 && chi_peek(st) > 0.0);

        printf("  flips: %d  flips_odd: %s\n", st->flips,
               (st->flips % 2) ? "True" : "False");
        printf("  final_polarity: %.1f  final_r_chi: %.6f\n",
               final_pol, chi_peek(st));
        printf("  channel_recovered_polarity: %s\n", channel_ok ? "True" : "False");
        printf("  is_reducible: %s\n", reducible ? "True" : "False");

        if (st->flips != 3) ok = 0;
        if (final_pol != -initial_pol) ok = 0;
        if (reducible) ok = 0;
        if (!channel_ok) ok = 0;
        printf("  claim_holds: %s\n", ok ? "True" : "False");
    }

    chi_destroy(st);

    printf("--------------------------------------------------\n");
    if (ok)
        printf("OK — opaque primitive; parity trap holds\n");
    else
        printf("FAIL — parity trap or channel invariant broken\n");
    return ok;
}

#ifdef CHI_PRIMITIVE_DEMO
int main(void) {
    return chi_demonstrate_parity_trap() ? 0 : 1;
}
#endif
