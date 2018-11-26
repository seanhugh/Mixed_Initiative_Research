import sympy
from sympy import *
from latex2sympy.process_latex import *

# effectively the model in MVC
# takes changes from the server (controller) and applies them to model

# state returned by these methods:
# - equation (to be displayed)
# - buttons (actions that can be taken from here)
# - rest, a sub-dictionary containing
#   - equation (the abstract model equation state)
#   - highlight (the zipper state indicating the acting subnode)

# generate new state from starting equation
def init(eq):
  # parse into sympy expressoin
  e = process_sympy(eq)

  return {
    "equation" : "0:\\quad " + sympy.latex(e),
    "buttons" : ["divide", "factor", "multiply"],
    "state" : {
      "equation" : {
        "srepr" : sympy.srepr(e),
        "count" : 0
      },
      "zipper" : []
    }
  }

# state taken by update:
# - equation (representing internal equation state)
# - zipper (representing state inside)

# generate updated state from old state and given view action
def update(action, state):
  e = eval(state["equation"]["srepr"]) # XXX LOL dangerous af
  count = state["equation"]["count"] + 1

  return {
    "equation" : str(count) + ":\\quad " + sympy.latex(e),
    "buttons" : ["divide", "factor", "multiply"],
    "state" : {
      "equation" : {
        "srepr" : sympy.srepr(e),
        "count" : count
      },
      "zipper" : []
    }
  }
