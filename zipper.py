import sympy
from sympy import *

# XXX need hole semantics library for this stuff
# esp when it comes to generating latex

# XXX we're only gonna support equality, addition, multiplication, power for now...

# tip of zipper -- the bottom level
def hd(l):
  return l[0]

# tail end of zipper -- rest of it
def tl(l):
  return l[1:]

def get_subexprs(e, zipper):
  if len(zipper) == 0:
    return [e]

  return get_subexprs(e.args[zipper[-1]], zipper[:-1]) + [e]


def non_empty(e):
  return e.args != ()

def commutative(e):
  return e.func == Add or e.func == Mul or e.func == Eq


def grandparent(e, zipper):
  se = get_subexprs(e, zipper)
  if len(se) < 3:
    return None
  return se[2]

def parent(e, zipper):
  se = get_subexprs(e, zipper)
  if len(se) < 2:
    return None
  return se[1]

def left_sib(e, zipper):
  se = get_subexprs(e, zipper)
  if len(se) < 2:
    return None
  loc = hd(zipper)
  if loc == 0:
    return None
  else:
    return se[1].args[loc - 1]

def right_sib(e, zipper):
  se = get_subexprs(e, zipper)
  if len(se) < 2:
    return None
  loc = hd(zipper)
  if loc == len(se[1].args) - 1:
    return None
  else:
    return se[1].args[loc + 1]


# match a list of nodes with list of predicates
def match_pre(l, c):
  for l, c in zip(l, c):
    if l == None:
      return False
    if not c(l.func):
      return False
  return True

def eq(c):
  def e(x):
    return c == x
  return e
