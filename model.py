import sympy
from ir import *
from latex2sympy.process_latex import *
from zipper import *

# effectively the model in MVC
# takes changes from the server (controller) and applies them to model

# what are the actions available at this location?
# XXX this would be so much better if our zippers were typed...
def get_actions(e, zipper, ac):
  se = get_subexprs(e, zipper)
  print("subexprs", se)

  actions = ["simplify", "expand"]

  tree_actions = []

  # collect movement actions
  if non_empty(hd(se)):
    tree_actions += ["down"]

  if len(zipper) != 0:
    tree_actions += ["up"]

  if not is_none(left_sib(e, zipper)):
    tree_actions += ["left"]
  if not is_none(right_sib(e, zipper)):
    tree_actions += ["right"]

  # if option 2 is active only return the simplify button
  if (ac == "false"):
    return [actions, []]

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

  print(actions, tree_actions)

  return [actions, tree_actions]

# apply an action at this location in an expression
def apply_action(act, e, zipper):
  se = get_subexprs(e, zipper)
  if act == "down":
    return e, [0] + zipper
  elif act == "up":
    return e, tl(zipper)
  elif act == "left":
    return e, [hd(zipper) - 1] + tl(zipper)
  elif act == "right":
    return e, [hd(zipper) + 1] + tl(zipper)
  elif act == "commute left":
    l = list(se[1].args)
    l = l[:zipper[0] - 1] + [l[zipper[0]], l[zipper[0] - 1]] + l[zipper[0] + 1:]

    e = fill(e, type(se[1])(*l), tl(zipper))
    zipper[0] = zipper[0] - 1

    return e, zipper
  elif act == "commute right":
    l = list(se[1].args)
    l = l[:zipper[0]] + [l[zipper[0] + 1], l[zipper[0]]] + l[zipper[0] + 2:]

    e = fill(e, type(se[1])(*l), tl(zipper))
    zipper[0] = zipper[0] + 1
    return e, zipper
  elif act == "distribute right":
    l = list(se[1].args)
    dist = Add(*[Mul(l[zipper[0]], i) for i in l[zipper[0] + 1].args])
    l = l[:zipper[0]] + [dist] + l[zipper[0] + 2:]
    return fill(e, type(se[1])(*l), tl(zipper)), tl(zipper)
  elif act == "sub from both sides":
    if se[1].__class__ == Eq:
      ths = se[1].args[zipper[0]]
      ohs = se[1].args[1 - zipper[0]]

      zipper[0] = 1 - zipper[0]
      e = fill(e, Add(ohs, Mul(Number(-1), ths)), zipper)
      zipper[0] = 1 - zipper[0]
      e = fill(e, Number(0), zipper)

      return e, tl(zipper)
    elif se[1].__class__ == Add:
      ohs = se[2].args[1 - zipper[1]]
      l = list(se[1].args)

      ohs = Add(ohs, Mul(Number(-1), l[zipper[0]]))
      l = l[:zipper[0]] + l[zipper[0] + 1:]

      tlz = tl(zipper)
      e = fill(e, Add(*l), tlz)
      tlz[0] = 1 - tlz[0]
      e = fill(e, ohs, tlz)

      return e, tl(zipper)
  elif act == "div from both sides":
    if se[1].__class__ == Eq:
      ths = se[1].args[zipper[0]]
      ohs = se[1].args[1 - zipper[0]]

      zipper[0] = 1 - zipper[0]
      e = fill(e, Mul(ohs, Pow(ths, Number(-1))), zipper)
      zipper[0] = 1 - zipper[0]
      e = fill(e, Number(1), zipper)

      return e, tl(zipper)
    elif se[1].__class__ == Mul:
      ohs = se[2].args[1 - zipper[1]]
      l = list(se[1].args)

      ohs = Mul(ohs, Pow(l[zipper[0]], Number(-1)))
      l = l[:zipper[0]] + l[zipper[0] + 1:]

      tlz = tl(zipper)
      e = fill(e, Mul(*l), tlz)
      tlz[0] = 1 - tlz[0]
      e = fill(e, ohs, tlz)

      return e, tl(zipper)
  elif act == "simplify":
    sp = se[0].to_sympy()
    spe = sp.doit()
    # attempt sympify; if it does nothing then simplify
    spe = sympy.sympify(spe)
    if spe == sp:
      spe = sympy.simplify(spe)
    return fill(e, ir_of_sympy(spe), zipper), zipper
  elif act == "expand":
    sp = se[0].to_sympy()
    spe = sympy.expand(se[0].to_sympy())
    return fill(e, ir_of_sympy(spe), zipper), zipper

  return e, zipper # do nothing for now


# super janky selection highlighting via hole punch
# really hope nobody names their variable ASDFHOLEASDF
def highlight_selection(e, zipper):
  se = get_subexprs(e, zipper)[0]
  return fill(e, Highlight(se), zipper).to_latex()

# state returned by these methods:
# - equation (to be displayed)
# - buttons (actions that can be taken from here)
# - rest, a sub-dictionary containing
#   - equation (the abstract model equation state)
#   - highlight (the zipper state indicating the acting subnode)

# generate new state from starting equation
def init(eq, ac):
  # parse into sympy expression
  e = process_sympy(eq)
  e = ir_of_sympy(e).flatten()

  return {
    "equation" : "0:\\quad " + highlight_selection(e, []),
    "buttons" : get_actions(e, [], ac),
    "state" : {
      "active" : ac,
      "equation" : {
        "srepr" : e.srepr(),
        "count" : 0,
        "raw_eq" : str(e.to_latex()),
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
  e2 = e2.flatten()
  count = state["equation"]["count"] + 1 # increment state

  ac = state["active"]

  return {
    "equation" : str(count) + ":\\quad " + highlight_selection(e2, zipper2),
    "buttons" : get_actions(e2, zipper2, ac),
    "active" : ac,
    "state" : {
      "active" : ac,
      "equation" : {
        "srepr" : e2.srepr(),
        "count" : count,
        "raw_eq" : str(e2.to_latex()),
      },
      "zipper" : zipper2
    }
  }

