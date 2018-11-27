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
  print("subexprs", se)

  actions = ["simplify"]

  # collect movement actions
  if non_empty(hd(se)):
    actions += ["move down"]

  if len(zipper) != 0:
    actions += ["move up"]

  if not is_none(left_sib(e, zipper)):
    actions += ["move left"]
  if not is_none(right_sib(e, zipper)):
    actions += ["move right"]

  # collect editing actions
  # commuting
  if match([parent(e, zipper)], [orp([is_a(Eq), is_a(Add), is_a(Mul)])]):
    print("actions")
    print(left_sib(e, zipper))
    print(right_sib(e, zipper))
    if not is_none(left_sib(e, zipper)):
      actions += ["commute left"]
    if not is_none(right_sib(e, zipper)):
      actions += ["commute right"]

  # distributing -- currently only when you're a term in a mul
  # and your right term is an add
  if match([parent(e, zipper), right_sib(e, zipper)], [is_a(Mul), is_a(Add)]):
    actions += ["distribute right"]

  # taking off of both sides of an equality
  if (match([grandparent(e, zipper), parent(e, zipper)],
            [is_a(Eq), is_a(Add)]) or
      match([grandparent(e, zipper), parent(e, zipper)],
            [is_none, is_a(Eq)])):
    actions += ["sub from both sides"]

  if (match([grandparent(e, zipper), parent(e, zipper)],
            [is_a(Eq), is_a(Mul)]) or
      match([grandparent(e, zipper), parent(e, zipper)],
            [is_none, is_a(Eq)])):
    actions += ["div from both sides"]

  return actions

# apply an action at this location in an expression
def apply_action(act, e, zipper):
  se = get_subexprs(e, zipper)
  if act == "move down":
    return e, [0] + zipper
  elif act == "move up":
    return e, tl(zipper)
  elif act == "move left":
    return e, [hd(zipper) - 1] + tl(zipper)
  elif act == "move right":
    return e, [hd(zipper) + 1] + tl(zipper)
  elif act == "commute left":
    l = list(se[1].args)
    l = l[:zipper[0] - 1] + [l[zipper[0]], l[zipper[0] - 1]] + l[zipper[0] + 1:]

    e = fill(e, se[1].func(*l), tl(zipper))
    zipper[0] = zipper[0] - 1

    return e, zipper
  elif act == "commute right":
    l = list(se[1].args)
    l = l[:zipper[0]] + [l[zipper[0] + 1], l[zipper[0]]] + l[zipper[0] + 2:]

    e = fill(e, se[1].func(*l), tl(zipper))
    zipper[0] = zipper[0] + 1
    return e, zipper
  elif act == "distribute right":
    l = list(se[1].args)
    dist = Add(*[Mul(l[zipper[0]], i) for i in l[zipper[0] + 1].args])
    l = l[:zipper[0]] + [dist] + l[zipper[0] + 2:]
    return fill(e, se[1].func(*l), tl(zipper)), tl(zipper)
  elif act == "sub from both sides":
    if se[1].func == Eq:
      ths = se[1].args[zipper[0]]
      ohs = se[1].args[1 - zipper[0]]

      zipper[0] = 1 - zipper[0]
      e = fill(e, Add(ohs, Mul(Integer(-1), ths)), zipper)
      zipper[0] = 1 - zipper[0]
      e = fill(e, Integer(0), zipper)

      return e, tl(zipper)
    elif se[1].func == Add:
      ohs = se[2].args[1 - zipper[1]]
      l = list(se[1].args)

      ohs = Add(ohs, Mul(Integer(-1), l[zipper[0]]))
      l = l[:zipper[0]] + l[zipper[0] + 1:]

      tlz = tl(zipper)
      e = fill(e, Add(*l), tlz)
      tlz[0] = 1 - tlz[0]
      e = fill(e, ohs, tlz)

      return e, tl(zipper)
  elif act == "div from both sides":
    if se[1].func == Eq:
      ths = se[1].args[zipper[0]]
      ohs = se[1].args[1 - zipper[0]]

      zipper[0] = 1 - zipper[0]
      e = fill(e, Mul(ohs, Pow(ths, Integer(-1))), zipper)
      zipper[0] = 1 - zipper[0]
      e = fill(e, Integer(1), zipper)

      return e, tl(zipper)
    elif se[1].func == Mul:
      ohs = se[2].args[1 - zipper[1]]
      l = list(se[1].args)

      ohs = Mul(ohs, Pow(l[zipper[0]], Integer(-1)))
      l = l[:zipper[0]] + l[zipper[0] + 1:]

      tlz = tl(zipper)
      e = fill(e, Mul(*l), tlz)
      tlz[0] = 1 - tlz[0]
      e = fill(e, ohs, tlz)

      print(e)

      return e, tl(zipper)
  elif act == "simplify":
    return fill(e, sympy.sympify(se[0]), zipper), zipper

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

