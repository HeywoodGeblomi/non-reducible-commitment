from chi_primitive.chi_primitive import ChiState
import random


class CommitmentGatedReconstruction:
    def __init__(self, horizon: int = 16, flip_prob: float = 0.15, seed: int = 42):
        self.horizon = horizon
        self.flip_prob = flip_prob
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.t = 0
        self.chi = ChiState()
        self.true_polarity = 1
        self.done = False
        self.total_reward = 0.0
        self.flip_count = 0
        return self._get_obs()

    def _generate_draft(self):
        draft_value = self.rng.randint(0, 1)
        aligned = (draft_value == (1 if self.true_polarity > 0 else 0))
        return {"draft_action": draft_value, "aligned": aligned}

    def _get_obs(self):
        return {
            "t": self.t,
            "obs": self.rng.randint(0, 2),
            "draft": self._generate_draft()
        }

    def step(self, action: int):
        if self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1

        obs = self._get_obs()
        draft = obs["draft"]

        if action == 1:  # ACCEPT
            reward = 1.0 if draft["aligned"] else -1.5
        else:            # REJECT
            reward = 0.4 if not draft["aligned"] else -0.8

        self.total_reward += reward
        self.t += 1
        if self.t >= self.horizon:
            self.done = True

        return obs, reward, self.done, {
            "true_polarity": self.true_polarity,
            "flip_count": self.flip_count,
            "chi_polarity": self.chi.polarity(),
            "r_chi": self.chi.reveal(0.20),
            "draft_aligned": draft["aligned"],
        }

    def optimal_action(self, obs, polarity=None, r_chi=None):
        draft = obs["draft"]
        if polarity is not None:
            needed = 1 if polarity > 0 else 0
        elif r_chi is not None:
            needed = 1 if r_chi > 0 else 0
        else:
            return 0

        return 1 if draft["draft_action"] == needed else 0
