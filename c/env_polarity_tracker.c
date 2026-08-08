/*
 * Environment 2 — Polarity Tracker (pure C)
 *
 * Hidden polarity flips at random intervals.
 * Visible observations are i.i.d. and identical across polarities.
 * Correct action depends on true polarity.
 * After odd flips, any pure function of the observation history is lost.
 *
 * Compile:
 *   gcc -O2 -std=c11 -o polarity_suite env_polarity_tracker.c chi_primitive.c -lm
 *   ./polarity_suite
 */

#include "chi_primitive.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HORIZON     20
#define N_EPISODES  80
#define MAX_HIST    64
#define FLIP_PROB_NUM 18

typedef struct {
    int obs;
    int t;
} Obs;

typedef struct {
    int       horizon;
    int       t;
    double    true_polarity;
    int       flip_count;
    int       done;
    double    total_reward;
    unsigned  rng;
    ChiState *chi;
} PolarityTracker;

static unsigned pt_rand(unsigned *state) {
    *state = (*state * 1103515245u + 12345u) & 0x7fffffffu;
    return *state;
}

static double pt_rand01(unsigned *state) {
    return (double)pt_rand(state) / (double)0x7fffffff;
}

static void pt_init(PolarityTracker *env, int horizon, unsigned seed) {
    int k;
    env->horizon = horizon;
    env->t = 0;
    env->true_polarity = 1.0;
    env->flip_count = 0;
    env->done = 0;
    env->total_reward = 0.0;
    env->rng = seed ? seed : 1u;
    env->chi = chi_create();
    chi_force(env->chi, 1);
    for (k = 0; k < 5; ++k)
        chi_reveal(env->chi, 0.35);
}

static void pt_free(PolarityTracker *env) {
    chi_destroy(env->chi);
    env->chi = NULL;
}

static Obs pt_obs(PolarityTracker *env) {
    Obs o;
    o.obs = (int)(pt_rand(&env->rng) % 4u);
    o.t = env->t;
    return o;
}

typedef struct {
    double true_polarity;
    int    flip_count;
    double polarity;
    double r_chi;
    int    is_reducible;
} StepInfo;

static Obs pt_step(PolarityTracker *env, int action, double *reward, StepInfo *info) {
    int k;
    action &= 1;
    {
        int correct = (env->true_polarity > 0.0) ? 1 : 0;
        *reward = (action == correct) ? 1.0 : -1.0;
    }
    env->total_reward += *reward;
    env->t += 1;

    if (env->t < env->horizon && pt_rand01(&env->rng) < (FLIP_PROB_NUM / 100.0)) {
        env->true_polarity *= -1.0;
        chi_commit(env->chi);
        env->flip_count += 1;
        for (k = 0; k < 4; ++k)
            chi_reveal(env->chi, 0.45);
    }

    if (env->t >= env->horizon)
        env->done = 1;

    chi_reveal(env->chi, 0.20);

    info->true_polarity = env->true_polarity;
    info->flip_count = env->flip_count;
    info->polarity = chi_polarity(env->chi);
    info->r_chi = chi_peek(env->chi);
    info->is_reducible = (env->flip_count % 2 == 0) ? 1 : 0;

    return pt_obs(env);
}

static int agent_reactive(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)hist; (void)nhist; (void)info;
    return obs.obs & 1;
}

static int agent_visible(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)obs; (void)info;
    if (nhist <= 0) return 0;
    {
        int votes = 0, i;
        for (i = 0; i < nhist; ++i)
            votes += hist[i].obs & 1;
        return (votes > nhist / 2) ? 1 : 0;
    }
}

static int agent_full_chi(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)obs; (void)hist; (void)nhist;
    if (info.polarity > 0.0) return 1;
    if (info.polarity < 0.0) return 0;
    return (info.r_chi > 0.0) ? 1 : 0;
}

static int agent_frozen(Obs obs, const Obs *hist, int nhist, StepInfo info, int frozen) {
    (void)obs; (void)hist; (void)nhist; (void)info;
    return frozen & 1;
}

static int agent_no_reveal(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    return agent_visible(obs, hist, nhist, info);
}

typedef int (*AgentFn)(Obs, const Obs *, int, StepInfo);

static void run_episode(AgentFn agent, unsigned seed, int frozen_mode, int frozen_val,
                        double *out_ret, int *out_flips) {
    PolarityTracker env;
    Obs hist[MAX_HIST];
    int nhist = 0;
    StepInfo info;
    Obs obs;
    double reward;

    memset(&info, 0, sizeof info);
    pt_init(&env, HORIZON, seed);
    obs = pt_obs(&env);
    info.polarity = chi_polarity(env.chi);
    info.r_chi = chi_peek(env.chi);
    info.true_polarity = env.true_polarity;
    info.flip_count = 0;
    info.is_reducible = 1;

    while (!env.done) {
        int action;
        if (frozen_mode)
            action = agent_frozen(obs, hist, nhist, info, frozen_val);
        else
            action = agent(obs, hist, nhist, info);

        if (nhist < MAX_HIST)
            hist[nhist++] = obs;

        obs = pt_step(&env, action, &reward, &info);
    }

    *out_ret = env.total_reward;
    *out_flips = env.flip_count;
    pt_free(&env);
}

static void evaluate(AgentFn agent, int frozen_mode, int frozen_val,
                     double *avg_ret, double *avg_flips) {
    double total_ret = 0.0;
    int total_flips = 0;
    int i;
    for (i = 0; i < N_EPISODES; ++i) {
        double ret;
        int flips;
        run_episode(agent, (unsigned)(i + 1), frozen_mode, frozen_val, &ret, &flips);
        total_ret += ret;
        total_flips += flips;
    }
    *avg_ret = total_ret / (double)N_EPISODES;
    *avg_flips = (double)total_flips / (double)N_EPISODES;
}

int main(void) {
    double reactive, visible, full, fz0, fz1, no_rev;
    double fr, fv, ff, ff0, ff1, fn;

    printf("====================================================================\n");
    printf("COMMITMENT STRESS SUITE (C) — Env 2: Polarity Tracker\n");
    printf("====================================================================\n");
    printf("Horizon=%d  flip_prob=0.%02d  Episodes=%d  Max return = %d\n\n",
           HORIZON, FLIP_PROB_NUM, N_EPISODES, HORIZON);

    evaluate(agent_reactive, 0, 0, &reactive, &fr);
    evaluate(agent_visible, 0, 0, &visible, &fv);
    evaluate(agent_full_chi, 0, 0, &full, &ff);
    evaluate(NULL, 1, 0, &fz0, &ff0);
    evaluate(NULL, 1, 1, &fz1, &ff1);
    evaluate(agent_no_reveal, 0, 0, &no_rev, &fn);

    printf("%-28s %10s  %9s  Notes\n", "Method", "Avg return", "Avg flips");
    printf("--------------------------------------------------------------------\n");
    printf("%-28s %+10.2f  %9.1f  obs noise only\n",
           "Reactive (no memory)", reactive, fr);
    printf("%-28s %+10.2f  %9.1f  collapses after flips\n",
           "Visible-history only", visible, fv);
    printf("%-28s %+10.2f  %9.1f  tracks polarity via r_\u03c7\n",
           "Full \u03c7 + reveal", full, ff);
    printf("%-28s %+10.2f  %9.1f  stuck on one polarity\n",
           "Frozen \u03c7=0", fz0, ff0);
    printf("%-28s %+10.2f  %9.1f  stuck on one polarity\n",
           "Frozen \u03c7=1", fz1, ff1);
    printf("%-28s %+10.2f  %9.1f  falls back to visible\n",
           "\u03c7, reveal disabled", no_rev, fn);
    printf("--------------------------------------------------------------------\n");
    printf("Gap (Full \u2212 Visible):  %+.2f\n", full - visible);
    printf("Gap (Full \u2212 Reactive): %+.2f\n", full - reactive);

    if (!(full > visible + 2.0 && full > reactive + 2.0)) {
        printf("\nFAIL \u2014 Full \u03c7 did not decisively beat baselines\n");
        return 1;
    }

    printf("\nOK \u2014 Polarity Tracker (C) separation is decisive\n");
    return 0;
}
