import sympy
from sympy import *
from latex2sympy.process_latex import *

# effectively the model in MVC
# takes changes from the server (controller) and applies them to model

# XXX need hole semantics library for this stuff
# esp when it comes to generating latex

# XXX we're only gonna support equality, addition, multiplication, power for now...

def get_subexprs(e, zipper):
  if len(zipper) == 0:
    return [e]

  return [e] + get_subexprs(e.args[zipper[0]], zipper[1:])

# what are the actions available at this location?
# XXX this would be so much better if our zippers were typed...
# XXX alas python doesn't have nice matching; but we could fix this
def get_actions(e, zipper):
  se = get_subexprs(e, zipper)

  actions = ["simplify"]

  # collect movement actions
  if se[-1].args != ():
    actions += ["move down"]

  if len(zipper) != 0:
    actions += ["move up"]

  if len(se) >= 2: # we are at least one expression in
    if zipper[-1] > 0:
      actions += ["move left"]
    if zipper[-1] < len(se[-2].args) - 1:
      actions += ["move right"]

  # collect editing actions
  # commuting
  if len(se) >= 2 and (se[-2].func == "Add" or se[-2].func == "Mul" or se[-2].func == "Eq"):
    if zipper[-1] > 0:
      actions += ["commute left"]
    if zipper[-1] < len(se[-2].args) - 1:
      actions += ["commute right"]

  # distributing -- currently only when you're a term in a mul
  # and your right term is an add
  if len(se) >= 2:
    if (se[-2].func == "Mul" and
        zipper[-1] < len(se[-2].args) - 1 and
        se[-2].args[zipper[-1] + 1].func == "Add"):
      actions += ["distribute"]

  # taking off of both sides of an equality
  if len(se) >= 3:
    if se[-3].func == "Eq":
      if se[-2].func == "Add":
        actions += ["sub from both sides"]
      elif se[-2].func == "Mul":
        actions += ["div from both sides"]

  return actions

# apply an action at this location in an expression
def apply_action(act, e, zipper):
  if act == "move down":
    return e, zipper + [0]
  elif act == "move up":
    return e, zipper[:-1]
  elif act == "move left":
    return e, zipper[:-1] + [zipper[-1] - 1]
  elif act == "move right":
    return e, zipper[:-1] + [zipper[-1] + 1]
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
    "equation" : str(count) + ":\\quad " + sympy.latex(e2) + " \\quad " + sympy.latex(get_subexprs(e2, zipper2)[-1]),
    "buttons" : get_actions(e2, zipper2),
    "state" : {
      "equation" : {
        "srepr" : sympy.srepr(e2),
        "count" : count
      },
      "zipper" : zipper2
    }
  }

