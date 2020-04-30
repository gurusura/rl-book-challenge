from nstep_sarsa import nStepSarsa
import numpy as np

class OffPolnStepSarsa(nStepSarsa):
  def __init__(self, env, b=None, step_size=0.1, gamma=0.9, n=1, eps=0.1):
    super().__init__(env, step_size, gamma, n, eps)
    self.b = self.uniform_pol() if b is None else b
    assert(self.is_soft(self.b))
    assert(0 < self.step_size <= 1)
    assert(n is None or n >= 2)

  def is_soft(self, pol):
    for s in self.env.states:
      for a in self.env.moves_d[s]:
        if pol[(a, s)] == 0:
          return False
    return True 

  def uniform_pol(self):
    return {(a, s): 1 / len(self.env.moves_d[s]) for s in self.env.states for a in self.env.moves_d[s]}

  def pol_eval(self, n_ep_train=100, pi=None, n_ep_test=170):
    pi_learned = pi is None
    n, R, S, Q, A = self.n, self.R, self.S, self.Q, self.A
    ro = np.ones(n - 1)
    self.pi = self.initialize_pi() if pi_learned else pi
    ep_per_t = [] 
    for ep in range(n_ep_train):
      print(f"ep #{ep}")
      S[0] = self.env.reset()
      A[0] = self.sample_action(self.pi, S[0])
      T = np.inf
      t = 0
      while True:
        ep_per_t.append(ep)
        tm, tp1m = t % (n + 1), (t + 1) % (n + 1)
        if t < T:
          S[tp1m], R[tp1m], d, _ = self.env.step(A[tm])
          if d:
            T = t + 1
          else:
            A[tp1m] = self.sample_action(self.b, S[tp1m])
            ro[(t + 1) % (n - 1)] = self.pi[(A[tp1m], S[tp1m])] / self.b[(A[tp1m], S[tp1m])]
        tau = t - n + 1
        if tau >= 0:
          if tau + n > T:
            ro[(tau + n - 1) % (n - 1)] = 1 
          is_ratio = ro.prod()
          G = self.n_step_return_q(tau, T)
          taum = tau % (n + 1)
          s, a = S[taum], A[taum]
          Q[(s, a)] += self.step_size * is_ratio * (G - Q[(s, a)])
          if pi_learned:
            self.update_pi(s)
        if tau == (T - 1):
          break
        t += 1
    return super().pol_eval(n_ep_test, self.pi)