import sympy
from sympy import *
from latex2sympy.process_latex import *
from zipper import *

# effectively the model in MVC
# takes changes from the server (controller) and applies them to model

# what are the actions available at this location?
# XXX this would be so much better if our zippers were typed...
def get_actions(e, zipper):
  se = get_subexprs(e, zipper)

  actions = ["simplify"]

  # collect movement actions
  if non_empty(hd(se)):
    actions += ["move down"]

  if len(zipper) != 0:
    actions += ["move up"]

  if left_sib(e, zipper):
    actions += ["move left"]
  if right_sib(e, zipper):
    actions += ["move right"]

  # collect editing actions
  # commuting
  if match_pre([parent(e, zipper)], [commutative]):
    if left_sib(e, zipper):
      actions += ["commute left"]
    if right_sib(e, zipper):
      actions += ["commute right"]

  # distributing -- currently only when you're a term in a mul
  # and your right term is an add
  if match_pre([parent(e, zipper), right_sib(e, zipper)], [eq(Mul), eq(Add)]):
    actions += ["distribute right"]

  # taking off of both sides of an equality
  if match_pre([grandparent(e, zipper), parent(e, zipper)], [eq(Eq), eq(Add)]):
    actions += ["sub from both sides"]

  if match_pre([grandparent(e, zipper), parent(e, zipper)], [eq(Eq), eq(Mul)]):
    actions += ["div from both sides"]

  return actions

# apply an action at this location in an expression
def apply_action(act, e, zipper):
  if act == "move down":
    return e, [0] + zipper
  elif act == "move up":
    return e, tl(zipper)
  elif act == "move left":
    return e, [hd(zipper) - 1] + tl(zipper)
  elif act == "move right":
    return e, [hd(zipper) + 1] + tl(zipper)
  else:
    return e, zipper # do nothing for now

# state returned by these methods:
# - equation (to be displayed)
# - buttons (actions that can be taken from here)
# - rest, a sub-dictionary containing
#   - equation (the abstract model equation state)
#   - highlight (the zipper state indicating the acting subnode)

# generate new state from starting equation
def init(eq):
  # parse into sympy expression
  e = process_sympy(eq)

  return {
    "equation" : "0:\\quad " + sympy.latex(e) + " \\quad top",
    "buttons" : get_actions(e, []),
    "state" : {
      "equation" : {
        "srepr" : sympy.srepr(e),
        "count" : 0
      },
      "zipper" : [] # starting at top level
    }
  }

# state taken by update:
# - equation (representing internal equation state)
# - zipper (representing state inside)

# generate updated state from old state and given view action
def update(action, state):
  e = eval(state["equation"]["srepr"]) # XXX LOL dangerous af
  zipper = state["zipper"]

  e2, zipper2 = apply_action(action, e, zipper) # apply action
  count = state["equation"]["count"] + 1 # increment state

  return {
    "equation" : str(count) + ":\\quad " + sympy.latex(e2) + " \\quad " + sympy.latex(get_subexprs(e2, zipper2)[0]),
    "buttons" : get_actions(e2, zipper2),
    "state" : {
      "equation" : {
        "srepr" : sympy.srepr(e2),
        "count" : count
      },
      "zipper" : zipper2
    }
  }

