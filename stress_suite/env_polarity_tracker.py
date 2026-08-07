from chi_primitive.chi_primitive import ChiState
import random


class PolarityTracker:
    def __init__(self, horizon: int = 20, flip_prob: float = 0.18, seed: int = 42):
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

    def _get_obs(self):
        return {"obs": self.rng.randint(0, 3), "t": self.t}

    def step(self, action: int):
        if self.rng.random() < self.flip_prob:
            self.true_polarity *= -1
            self.chi.commit()
            self.flip_count += 1

        correct = 1 if self.true_polarity > 0 else 0
        reward = 1.0 if action == correct else -1.0

        self.total_reward += reward
        self.t += 1
        if self.t >= self.horizon:
            self.done = True

        return self._get_obs(), reward, self.done, {
            "true_polarity": self.true_polarity,
            "flip_count": self.flip_count,
            "chi_polarity": self.chi.polarity(),
            "r_chi": self.chi.reveal(0.20),
        }

    def optimal_action(self, obs, polarity=None, r_chi=None):
        if polarity is not None:
            return 1 if polarity > 0 else 0
        if r_chi is not None:
            return 1 if r_chi > 0 else 0
        return 0
