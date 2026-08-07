from chi_primitive.chi_primitive import ChiState
import random


class IrreversibleDoor:
    def __init__(self, horizon: int = 12, seed: int = 42):
        self.horizon = horizon
        self.rng = random.Random(seed)
        self.reset()

    def reset(self):
        self.t = 0
        self.true_door = None
        self.chi = ChiState()
        self.done = False
        self.total_reward = 0.0
        return self._get_obs()

    def _get_obs(self):
        if self.true_door is None:
            return {"phase": "choose", "obs": 0}
        return {"phase": "act", "obs": self.rng.randint(0, 1)}

    def step(self, action: int):
        reward = 0.0

        if self.t == 0:
            self.true_door = action
            self.chi.commit()
            if action == 1:
                self.chi.commit()
        else:
            correct = self.true_door
            reward = 1.0 if action == correct else -1.0

        self.total_reward += reward
        self.t += 1
        if self.t >= self.horizon:
            self.done = True

        return self._get_obs(), reward, self.done, {
            "true_door": self.true_door,
            "chi_polarity": self.chi.polarity(),
            "r_chi": self.chi.reveal(0.20),
        }

    def optimal_action(self, obs, polarity=None, r_chi=None):
        if obs["phase"] == "choose":
            return self.rng.randint(0, 1)
        if polarity is not None:
            return 1 if polarity > 0 else 0
        if r_chi is not None:
            return 1 if r_chi > 0 else 0
        return 0
