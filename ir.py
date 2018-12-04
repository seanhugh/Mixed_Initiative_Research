import sympy

# thin cover of subset of sympy
# so we have control over automatic operations
# preventing sympy's normal-form rewriting for instance

# convert sympy expr to IR
def ir_of_sympy(e):
#  if isinstance(e, sympy.StrictLessThan):
#    retval = LessThan(e.args)
#  elif isinstance(e, sympy.LessThan):
#    retval = LessThanOrEq(e.args)
#  elif isinstance(e, sympy.StrictGreaterThan):
#    retval = GreaterThan(e.args)
#  elif isinstance(e, sympy.GreaterThan):
#    retval = GreaterThanOrEq(e.args)
  if isinstance(e, sympy.Eq):
    retval = Eq(*list(map(ir_of_sympy, e.args)))
  elif isinstance(e, sympy.Number):
    if e.is_integer:
      retval = Number(int(e.evalf()))
    elif isinstance(e, sympy.Rational):
      nd = e.as_numer_denom()
      retval = Mul(Number(int(nd[0].evalf())), Pow(Number(int(nd[1].evalf())), Number(-1)))
    else:
      retval = Number(e.evalf()) # any other cases?
  elif isinstance(e, sympy.Symbol):
    retval = Symbol(e.name)
  elif isinstance(e, sympy.Add):
    retval = Add(*list(map(ir_of_sympy, e.args)))
  elif isinstance(e, sympy.Mul):
    retval = Mul(*list(map(ir_of_sympy, e.args)))
  elif isinstance(e, sympy.Pow):
    if isinstance(e.args[1], sympy.Rational) and e.args[1].as_numer_denom()[0] == 1:
      retval = Root(ir_of_sympy(e.args[0]), ir_of_sympy(e.args[1].as_numer_denom()[1]))
    else:
      retval = Pow(*list(map(ir_of_sympy, e.args)))
  elif isinstance(e, sympy.log):
    retval = Log(ir_of_sympy(e.args[0])) # handling other bases?
  elif isinstance(e, sympy.Derivative):
    nth = int(e.args[1][1].evalf())
    v = ir_of_sympy(e.args[1][0])
    retval = ir_of_sympy(e.args[0])
    for i in range(nth):
      retval = Derivative(retval, v)
  elif isinstance(e, sympy.Function):
    retval = Function(e.__class__.__name__, *list(map(ir_of_sympy, e.args)))
  else:
    raise Exception("unrecognized sympy class!")
  return retval

# should expose: .args, .flatten(), .to_sympy(), .to_latex()
class AstNode:
  def __init__(self, *args):
    self.args = tuple(args)
    self.is_neg = False

  def flatten(self):
    return type(self)(*list(map(lambda i: i.flatten(), self.args)))

  def to_sympy(self):
    raise Exception("unimplemented to_sympy!")

  # special provisions for making highlight transparent
  def unfold(self):
    return self

  # assoc is binding strength of caller
  # if assoc is higher than your associativity, then you should parenthesize
  # e.g. mul will call down with assoc=10 or something
  def to_latex(self, assoc=0):
    raise Exception("unimplemented to_latex!")

  def srepr(self):
    return self.__class__.__name__ + "(" + ",".join(list(map(lambda i: i.srepr(), self.args))) + ")"

class Eq(AstNode):
  def to_sympy(self):
    return sympy.Eq(*list(map(lambda i: i.to_sympy(), self.args)))
  def to_latex(self, assoc=0):
    return self.args[0].to_latex() + " = " + self.args[1].to_latex()

class Number(AstNode):
  def __init__(self, n):
    super().__init__()
    self.n = abs(n)
    self.is_neg = n < 0
  def srepr(self):
    return "Number(" + self.to_latex() + ")"
  def flatten(self):
    return Number(-self.n if self.is_neg else self.n)
  def to_sympy(self):
    return sympy.Number(-self.n if self.is_neg else self.n)
  def to_latex(self, assoc=0):
    return ("-" if self.is_neg else "") + str(self.n)

class Symbol(AstNode):
  def __init__(self, text):
    super().__init__()
    self.text = text
  def srepr(self):
    return "Symbol(\"" + self.text + "\")"
  def flatten(self):
    return self
  def to_sympy(self):
    return sympy.Symbol(self.text)
  def to_latex(self, assoc=0):
    return sympy.latex(self.to_sympy())

class Add(AstNode):
  # flatten out nested adds
  def flatten(self):
    new_args = []
    for i in self.args:
      i = i.flatten()
      if isinstance(i, Add):
        new_args += list(i.args)
      else:
        new_args += [i]
    if len(new_args) == 1:
      return new_args[0]
    else:
      return Add(*new_args)

  def to_sympy(self):
    print(list(map(lambda i: i.to_sympy(), list(self.args))))
    return sympy.Add(*list(map(lambda i: i.to_sympy(), list(self.args))))

  def to_latex(self, assoc=0):
    contents = ""
    for i in self.args:
      # special handling for negations
      if i.unfold().is_neg and not isinstance(i.unfold(), Number):
        contents += " - " + i.to_latex()
      elif i.unfold().is_neg and isinstance(i.unfold(), Number):
        contents += i.to_latex()
      elif contents == "":
        contents = i.to_latex()
      else:
        contents += " + " + i.to_latex()

    if assoc > 0:
      contents = "\\left(" + contents + "\\right)"
    return contents

class Mul(AstNode):
  # flatten out nested mul
  def flatten(self):
    new_args = []
    neg = False
    for i in self.args:
      i = i.flatten()

      if i.is_neg:
        i.is_neg = False
        neg = not neg

      if isinstance(i, Number) and i.n == 1:
        continue

      if isinstance(i, Mul):
        new_args += list(i.args)
      else:
        new_args += [i]

    if len(new_args) == 1:
      res = new_args[0]
    else:
      res = Mul(*new_args)
    
    res.is_neg = neg
    return res

  def to_sympy(self):
    return sympy.Mul(*list(map(lambda i: i.to_sympy(), self.args)))

  def to_latex(self, assoc=0):
    num_contents = ""
    den_contents = ""

    for i in self.args:
      # special handling for inversions
      if isinstance(i.unfold(), Pow) and i.unfold().args[1].is_neg:
        den_contents += " " + i.args[0].to_latex(10)
      elif isinstance(i.unfold(), Number) and num_contents != "":
        num_contents += " \\cdot " + i.to_latex(10)
      else:
        num_contents += " " + i.to_latex(10)

    if den_contents == "":
      res = num_contents
    else:
      res = "\\frac{" + num_contents + "}{" + den_contents + "}"

    if assoc > 10:
      res = "\\left(" + res + "\\right)"

    return res

class Pow(AstNode):
  def __init__(self, base, exponent):
    super().__init__(base, exponent)

  def to_sympy(self):
    return sympy.Pow(*list(map(lambda i: i.to_sympy(), self.args)))
  def to_latex(self, assoc=0):
    return self.args[0].to_latex(100) + "^{" + self.args[1].to_latex() + "}"

# special for powers of 1/something
class Root(AstNode):
  def __init__(self, expr, radix):
    super().__init__(expr, radix)

  def to_sympy(self):
    return sympy.root(*list(map(lambda i: i.to_sympy(), self.args)))
  def to_latex(self, assoc=0):
    if self.args[1].unfold().n != 2:
      return "\\sqrt[" + self.args[1].to_latex() + "]{" + self.args[0].to_latex() + "}"
    else:
      return "\\sqrt{" + self.args[0].to_latex() + "}"

class Log(AstNode):
  def to_sympy(self):
    return sympy.log(self.args[0], sympy.E)
  def to_latex(self, assoc=0):
    return "\\log{\\left(" + self.args[0].to_latex() + "\\right)}"

class Derivative(AstNode):
  def to_sympy(self):
    return sympy.Derivative(self.args[0].to_sympy(), (self.args[1].to_sympy(), 1))
  def to_latex(self, assoc=0):
    return "\\frac{d}{d" + self.args[1].to_latex() + "}" + self.args[0].to_latex()

class Function(AstNode):
  def __init__(self, name, *args):
    super().__init__(*args)
    self.name = name

  def srepr(self):
    return self.__class__.__name__ + "(\"" + self.name + "\"," + ",".join(list(map(lambda i: i.srepr(), self.args))) + ")"

  def flatten(self):
    return Function(self.name, *list(map(lambda i: i.flatten(), self.args)))

  def to_sympy(self):
    return getattr(sympy.functions, self.name)(*list(map(lambda i: i.to_sympy(), self.args)))

  def to_latex(self, assoc=0):
    return "\\" + self.name + "\\left(" + ",".join(list(map(lambda i: i.to_latex(), self.args))) + "\\right)"

# no-op highlighter node
class Highlight(AstNode):
  def unfold(self):
    return self.args[0]
  def srepr(self):
    return self.args[0].srepr()
  def to_sympy(self):
    return self.args[0].to_sympy()
  def to_latex(self, assoc=0):
    return "\\textcolor{red}{" + self.args[0].to_latex(assoc) + "}"

# possibly unused...
# class Neg(AstNode):
#   def __init__(self, e):
#     super().__init__(e)
# 
#   def flatten(self):
#     # apply negations to nested additions
#     if isinstance(self.args[0], Add):
#       new_args = []
#       for i in self.args[0].args:
#         new_args += [Neg(i)]
#       return Add(*new_args).flatten()
#     # double-negation cancels
#     elif isinstance(self.args[0], Neg):
#       return self.args[0].args[0]
#     else:
#       return self
# 
#   def to_sympy(self):
#     return sympy.Mul(-1, self.args[0].to_sympy())
#   def to_latex(self, assoc=0):
#     return "- " + self.args[0].to_latex(10)
# 
# class Inv(AstNode):
#   def __init__(self, e):
#     super().__init__(e)
# 
#   def flatten(self):
#     # apply inversion to nested multiplication
#     if isinstance(self.args[0], Mul):
#       new_args = []
#       for i in self.args[0].args:
#         new_args += [Inv(i)]
#       return Mul(*new_args).flatten()
#     # double-inversion cancels
#     elif isinstance(self.args[0], Inv):
#       return self.args[0].args[0]
#     else:
#       return self
# 
#   def to_sympy(self):
#     return sympy.Pow(self.args[0].to_sympy(), -1)
#   def to_latex(self, assoc=0):
#     return "\\frac{1}{" + self.args[0].to_latex() + "}"
# 
# class Integral(AstNode):
#   def to_sympy(self):
#     if len(self.args) == 4:
#       return sympy.Integral(self.args[0].to_sympy(), (self.args[1].to_sympy(), self.args[2].to_sympy(), self.args[3].to_sympy()))
#     else:
#       return sympy.Integral(self.args[0].to_sympy(), self.args[1].to_sympy())
#   def to_latex(self):
#     if len(self.args) == 4:
#       return "\\int_{" + self.args[2].to_latex() + "}^{" + self.args[3].to_latex() + "}" + self.args[0].to_latex() + " d" + self.args[1].to_latex()
#     else:
#       return "\\int" + self.args[0].to_latex() + "d" + self.args[1].to_latex()
# 
# class Sqrt(AstNode):
#   def to_sympy(self):
#     return sympy.Sqrt(*map(lambda i: i.to_sympy(), self.args))
#   def to_latex():
#     return "\\sqrt{" + self.args[0].to_latex() + "}"
# 
# class LessThan(AstNode):
#   def __init__(self, lh, rh):
#     super().__init__(lh, rh)
#   def to_sympy(self):
#     return sympy.StrictLessThan(*map(lambda i: i.to_sympy(), self.args))
#   def to_latex(self, assoc=0):
#     return self.args[0].to_latex() + " \lt " + self.args[1].to_latex()
# 
# class LessThanOrEq(AstNode):
#   def __init__(self, lh, rh):
#     super().__init__(lh, rh)
#   def to_sympy(self):
#     return sympy.LessThan(*map(lambda i: i.to_sympy(), self.args))
#   def to_latex(self, assoc=0):
#     return self.args[0].to_latex() + " \leq " + self.args[1].to_latex()
# 
# class GreaterThan(AstNode):
#   def __init__(self, lh, rh):
#     super().__init__(lh, rh)
#   def to_sympy(self):
#     return sympy.StrictGreaterThan(*map(lambda i: i.to_sympy(), self.args))
#   def to_latex(self, assoc=0):
#     return self.args[0].to_latex() + " \gt " + self.args[1].to_latex()
# 
# class GreaterThanOrEq(AstNode):
#   def __init__(self, lh, rh):
#     super().__init__(lh, rh)
#   def to_sympy(self):
#     return sympy.GreaterThan(*map(lambda i: i.to_sympy(), self.args))
#   def to_latex(self, assoc):
#     return self.args[0].to_latex() + " \geq " + self.args[1].to_latex()
# 
