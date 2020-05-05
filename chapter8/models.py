import copy

class Model:
  def __init__(self, states=None, moves_d=None):
    self.states = set() if states is None else set(states)
    self.moves_d = {s: set() for s in self.states} if moves_d is None else moves_d
    self.trans = {}

  def add_transition(self, s, a, r, s_p):
    self.states.add(s)
    if s in self.moves_d:
      self.moves_d[s].add(a)
    else:
      self.moves_d[s] = set([a])
    self.trans[(s, a)] = (s_p, r)

  def sample_s_r(self, s, a):
    try:
      return self.trans[(s, a)]
    except KeyError:
      print(f"transition {s}, {a} doesn't exist yet")

  def __str__(self):
    strg = ''
    for s in self.states:
      strg += str(s) + '\n'
      for a in self.moves_d[s]:
        strg += f"->{a}\n"
    return strg

  def reset(self):
    self.trans = {}


class FullModel(Model):
  def __init__(self, env):
    super().__init__(env.states, env.moves_d)
    self.env = copy.copy(env)

  def sample_s_r(self, s, a):
    self.env.force_state(s)
    s_p, r, _, _ = self.env.step(a)
    return s_p, r 
