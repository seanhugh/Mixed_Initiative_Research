import sympy

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
  return {
    "equation" : "$$" + eq + "0$$",
    "buttons" : ["divide", "factor", "multiply"],
    "state" : {
      "equation" : (eq, 0),
      "zipper" : []
    }
  }

# state taken by update:
# - equation (representing internal equation state)
# - zipper (representing state inside)

# generate updated state from old state and given view action
def update(action, state):
  eq = state["equation"][0]
  count = state["equation"][1]

  return {
    "equation" : "$$" + eq + str(count + 1) +  "$$",
    "buttons" : ["divide", "factor", "multiply", "do"+str(count + 1)],
    "state" : {
      "equation" : (eq, count + 1),
      "zipper" : []
    }
  }
