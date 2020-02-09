import numpy as np


class DynamicProgramming:
  def __init__(self, env, pi={}, theta=1e-4, gamma=0.9):
    self.theta = theta
    self.env = env  # environment with transitions p
    self.V = {tuple(s): 0 for s in self.env.states}
    self.gamma = gamma
    self.pi = pi

  def initialize_deterministic_pi(self):
    """Initializes a deterministic policy pi."""
    arb_d = {s: np.random.randint(len(self.env.moves)) for s in self.env.states}
    for s in self.env.states:
      for a in self.env.moves:
        self.pi[(a, s)] = int(a == self.env.moves[arb_d[s]])

  def print_policy(self):
    to_print = [[None] * self.env.size for _ in range(self.env.size)]
    max_length = max([len(move_name) for move_name in self.env.moves])
    for x in range(self.env.size):
      for y in range(self.env.size):
        to_print[x][y] = str(self.deterministic_pi((x, y))).ljust(max_length)
    print(*to_print, sep='\n')

  def print_values(self):
    np.set_printoptions(2)
    to_print = np.zeros((self.env.size, self.env.size))
    for x in range(self.env.size):
      for y in range(self.env.size):
        to_print[x][y] = self.V[(x, y)]
    print(to_print)

  def expected_value(self, s, a):
    # print(f"from state {s} action {a}")
    # for s_p in self.env.states:
    #   for r in self.env.r:
    #     val = self.env.p(s_p, r, s, a) * (r + self.gamma * self.V[s_p])
    #     if val != 0:
    #       print(f"p={self.env.p(s_p, r, s, a)}, r={r}, V[{s_p}]={self.V[s_p]}")
    return np.sum([self.env.p(s_p, r, s, a) *
                            (r + self.gamma * self.V[s_p])
                            for s_p in self.env.states for r in self.env.r])

  def policy_evaluation(self):
    """Updates V according to current pi."""
    while True:
      delta = 0
      for s in self.env.states:
        # print("self.pi =", [self.pi[(a, s)] for a in self.env.moves])
        # print("expected values =", [self.expected_value(s, a) for a in self.env.moves])
        v = self.V[s]
        self.V[s] = np.sum([self.pi[(a, s)] * self.expected_value(s, a)
                                   for a in self.env.moves])
        # print(f"self.V[{s}] = {np.sum([self.pi[(a, s)] * self.expected_value(s, a) for a in self.env.moves])}")
        delta = max(delta, abs(v-self.V[s]))
      if delta < self.theta:
        break

  def deterministic_pi(self, s):
    return self.env.moves[np.argmax([self.pi[(a, s)] for a in self.env.moves])]

  def update_pi(self, s, a):
    """Sets pi(a|s) = 1 and pi(a'|s) = 0 for a' != a."""
    for a_p in self.env.moves:
      self.pi[(a_p, s)] = (a == a_p)

  def policy_improvement(self):
    """Improves pi according to current V. Returns True if policy is stable."""
    policy_stable = True
    for s in self.env.states:
      old_action = self.deterministic_pi(s)
      self.update_pi(s, self.env.moves[np.argmax([self.expected_value(s, a) for a in self.env.moves])])
      policy_stable = policy_stable and (old_action == self.deterministic_pi(s))
    return policy_stable

  def policy_iteration(self):
    if not self.pi:
      self.initialize_deterministic_pi()

    while True:
      self.print_values()
      self.policy_evaluation()
      if self.policy_improvement():
        return self.V, self.pi