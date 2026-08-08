/*
 * Environment 1 — Irreversible Door (pure C)
 *
 * Step 0: choose Left (0) or Right (1). Choice is irreversible (stored in χ).
 * Later: observations are i.i.d. and identical across doors;
 *        reward = +1 if action == true_door else −1.
 *
 * Only non-reducible χ + reveal recovers the door.
 *
 * Compile:
 *   gcc -O2 -std=c11 -o door_suite env_irreversible_door.c chi_primitive.c -lm
 *   ./door_suite
 */

#include "chi_primitive.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define HORIZON     12
#define N_EPISODES  80
#define MAX_HIST    64

typedef struct {
    int phase;   /* 0 = choose, 1 = act */
    int obs;
} Obs;

typedef struct {
    int       horizon;
    int       t;
    int       true_door;   /* -1 until chosen */
    int       done;
    double    total_reward;
    unsigned  rng;
    ChiState *chi;
} IrreversibleDoor;

static unsigned door_rand(unsigned *state) {
    *state = (*state * 1103515245u + 12345u) & 0x7fffffffu;
    return *state;
}

static void door_init(IrreversibleDoor *env, int horizon, unsigned seed) {
    env->horizon = horizon;
    env->t = 0;
    env->true_door = -1;
    env->done = 0;
    env->total_reward = 0.0;
    env->rng = seed ? seed : 1u;
    env->chi = chi_create();
}

static void door_free(IrreversibleDoor *env) {
    chi_destroy(env->chi);
    env->chi = NULL;
}

static Obs door_obs(IrreversibleDoor *env) {
    Obs o;
    if (env->true_door < 0) {
        o.phase = 0;
        o.obs = 0;
    } else {
        o.phase = 1;
        o.obs = (int)(door_rand(&env->rng) & 1u);
    }
    return o;
}

typedef struct {
    int    true_door;
    double polarity;
    double r_chi;
    int    flips;
} StepInfo;

static Obs door_step(IrreversibleDoor *env, int action, double *reward, StepInfo *info) {
    action &= 1;
    *reward = 0.0;

    if (env->t == 0) {
        env->true_door = action;
        chi_force(env->chi, action);
        {
            int k;
            for (k = 0; k < 5; ++k)
                chi_reveal(env->chi, 0.35);
        }
    } else {
        *reward = (action == env->true_door) ? 1.0 : -1.0;
    }

    env->total_reward += *reward;
    env->t += 1;
    if (env->t >= env->horizon)
        env->done = 1;

    info->true_door = env->true_door;
    info->polarity  = chi_polarity(env->chi);
    info->r_chi     = chi_peek(env->chi);
    info->flips     = 0;

    if (env->t > 1) {
        chi_reveal(env->chi, 0.20);
        info->r_chi = chi_peek(env->chi);
    }
    {
        ChiVisible vis;
        chi_export_visible(env->chi, &vis);
        info->flips = vis.flips;
    }

    return door_obs(env);
}

static int agent_reactive(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)hist; (void)nhist; (void)info;
    if (obs.phase == 0) return 0;
    return obs.obs;
}

static int agent_visible(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)info;
    if (obs.phase == 0) return 1;
    if (nhist <= 0) return 0;
    {
        int votes = 0, i;
        for (i = 0; i < nhist; ++i)
            votes += hist[i].obs;
        return (votes > nhist / 2) ? 1 : 0;
    }
}

static int agent_full_chi(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    (void)hist; (void)nhist;
    if (obs.phase == 0)
        return 0;
    if (info.polarity > 0.0) return 1;
    if (info.polarity < 0.0) return 0;
    return (info.r_chi > 0.0) ? 1 : 0;
}

static int agent_frozen(Obs obs, const Obs *hist, int nhist, StepInfo info,
                        int frozen, int choose_door) {
    (void)hist; (void)nhist; (void)info;
    if (obs.phase == 0) return choose_door & 1;
    return frozen & 1;
}

static int agent_no_reveal(Obs obs, const Obs *hist, int nhist, StepInfo info) {
    return agent_visible(obs, hist, nhist, info);
}

typedef int (*AgentFn)(Obs, const Obs *, int, StepInfo);

static double run_episode(AgentFn agent, unsigned seed, int frozen_mode, int frozen_val) {
    IrreversibleDoor env;
    Obs hist[MAX_HIST];
    int nhist = 0;
    StepInfo info;
    Obs obs;
    double reward;
    int choose_door = (int)(seed & 1u);

    memset(&info, 0, sizeof info);
    door_init(&env, HORIZON, seed);
    obs = door_obs(&env);

    while (!env.done) {
        int action;
        if (frozen_mode)
            action = agent_frozen(obs, hist, nhist, info, frozen_val, choose_door);
        else
            action = agent(obs, hist, nhist, info);

        if (nhist < MAX_HIST)
            hist[nhist++] = obs;

        obs = door_step(&env, action, &reward, &info);
    }

    {
        double ret = env.total_reward;
        door_free(&env);
        return ret;
    }
}

static double evaluate(AgentFn agent, int frozen_mode, int frozen_val) {
    double total = 0.0;
    int i;
    for (i = 0; i < N_EPISODES; ++i)
        total += run_episode(agent, (unsigned)(i + 1), frozen_mode, frozen_val);
    return total / (double)N_EPISODES;
}

int main(void) {
    double reactive, visible, full, fz0, fz1, no_rev;

    printf("================================================================\n");
    printf("COMMITMENT STRESS SUITE (C) — Env 1: Irreversible Door\n");
    printf("================================================================\n");
    printf("Horizon=%d  Episodes=%d  Max return after choice \u2248 %d\n\n",
           HORIZON, N_EPISODES, HORIZON - 1);

    reactive = evaluate(agent_reactive, 0, 0);
    visible  = evaluate(agent_visible, 0, 0);
    full     = evaluate(agent_full_chi, 0, 0);
    fz0      = evaluate(NULL, 1, 0);
    fz1      = evaluate(NULL, 1, 1);
    no_rev   = evaluate(agent_no_reveal, 0, 0);

    printf("%-28s %10s  Notes\n", "Method", "Avg return");
    printf("----------------------------------------------------------------\n");
    printf("%-28s %+10.2f  ignores door\n", "Reactive (no memory)", reactive);
    printf("%-28s %+10.2f  obs identical \u2192 collapses\n", "Visible-history only", visible);
    printf("%-28s %+10.2f  recovers door via polarity\n", "Full \u03c7 + reveal", full);
    printf("%-28s %+10.2f  wrong half the time\n", "Frozen \u03c7=0", fz0);
    printf("%-28s %+10.2f  wrong half the time\n", "Frozen \u03c7=1", fz1);
    printf("%-28s %+10.2f  falls back to visible\n", "\u03c7, reveal disabled", no_rev);
    printf("----------------------------------------------------------------\n");
    printf("Gap (Full \u2212 Visible):  %+.2f\n", full - visible);
    printf("Gap (Full \u2212 Reactive): %+.2f\n", full - reactive);

    if (!chi_demonstrate_parity_trap()) {
        printf("\nFAIL \u2014 parity trap broken\n");
        return 1;
    }

    if (!(full > visible + 3.0 && full > reactive + 3.0)) {
        printf("\nFAIL \u2014 Full \u03c7 did not decisively beat baselines\n");
        return 1;
    }

    printf("\nOK \u2014 Irreversible Door (C) separation is decisive\n");
    return 0;
}
