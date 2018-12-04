from ir import *

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


# replace zipper-selected expression with given subexpression
def fill(e, se, zipper):
  if len(zipper) == 0:
    return se

  l = list(e.args)
  l[zipper[-1]] = fill(l[zipper[-1]], se, zipper[:-1])

  return type(e)(*l)

def non_empty(e):
  return e.args != ()


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
def match(l, c):
  for l, c in zip(l, c):
    if not c(l):
      return False
  return True

def is_a(c):
  def e(x):
    if x == None:
      return False
    return x.__class__ == c
  return e

def is_none(x):
  return x == None

def orp(l):
  def e(x):
    if x == None:
      return False
    for p in l:
      if p(x):
        return True
    return False
  return e
