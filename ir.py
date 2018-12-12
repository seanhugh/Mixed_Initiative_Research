import sympy

# thin cover of subset of sympy
# so we have control over automatic operations
# preventing sympy's normal-form rewriting for instance

# convert sympy expr to IR
def ir_of_sympy(e):
  if isinstance(e, sympy.Eq):
    retval = Eq(*list(map(ir_of_sympy, e.args)))

  elif isinstance(e, sympy.Number):
    if e.is_integer:
      retval = Number(int(e.evalf()))
    elif isinstance(e, sympy.Rational):
      nd = e.as_numer_denom()
      retval = Mul(Number(int(nd[0].evalf())), Number(int(nd[1].evalf())).invert())
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

  #print("=========================")
  #print(sympy.srepr(e))
  #print(retval.srepr())
  #print(retval.flatten().srepr())

  return retval.flatten()

# should expose: .args, .flatten(), .to_sympy(), .to_latex()
class AstNode:
  def __init__(self, *args):
    self.args = tuple(args)
    self.is_neg = False

  # default: flatten arguments
  def flatten(self):
    return type(self)(*list(map(lambda i: i.flatten(), self.args)))

  def to_sympy(self):
    raise Exception("unimplemented to_sympy!")

  # special provisions for making highlight transparent
  def unfold(self):
    return self

  # 1/self: mostly wraps; pow might unwrap; highlight must recurse
  def invert(self):
    return Pow(self, Number(-1))

  # assoc is binding strength of caller
  # if assoc is higher than your associativity, then you should parenthesize
  # e.g. mul will call down with assoc=10 or something
  # XXX suppress negations: everyone should handle their negated arguments
  def to_latex(self, assoc=0):
    raise Exception("unimplemented to_latex!")

  # default: own name + arguments
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
    self.n = n
    self.is_neg = n < 0
  def srepr(self):
    return "Number(" + str(self.n) + ")"
  def flatten(self):
    return Number(self.n)
  def to_sympy(self):
    return sympy.Number(self.n)
  def to_latex(self, assoc=0):
    return str(abs(self.n))

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
  def flatten(self):
    new_args = []
    for i in self.args:
      i = i.flatten()
      # flatten out nested adds
      if isinstance(i, Add):
        new_args += list(i.args)
      else:
        new_args += [i]

    # single-argument add: become the argument
    if len(new_args) == 1:
      return new_args[0]
    else:
      return Add(*new_args)

  def to_sympy(self):
    return sympy.Add(*list(map(lambda i: i.to_sympy(), list(self.args))))

  def to_latex(self, assoc=0):
    contents = ""
    for i in self.args:
      # special handling for negations
      if i.unfold().is_neg:
        contents += "-" + i.to_latex()
      elif contents == "":
        contents = i.to_latex()
      else:
        contents += " + " + i.to_latex()

    if assoc > 0:
      contents = "\\left(" + contents + "\\right)"
    return contents

class Mul(AstNode):
  def __init__(self, *args, neg=False):
    self.args = tuple(args)
    self.neg = neg # saved negativity
    
    # accumulate negativity
    for i in self.args:
      if i.is_neg:
        neg = not neg
    self.is_neg = neg

  # flatten out nested mul
  def flatten(self):
    new_args = []
    neg = self.neg # accumulate hidden negativity
    for i in self.args:
      i = i.flatten()

      # flatten multiply by one
      if isinstance(i, Number) and i.n == 1:
        continue
      if isinstance(i, Number) and i.n == -1:
        neg = not neg
        continue

      # flatten nested multiply
      if isinstance(i, Mul):
        new_args += list(i.args)
      else:
        new_args += [i]

    # single-argument mul: become the argument
    if len(new_args) == 1 and not neg:
      res = new_args[0]
    else:
      res = Mul(*new_args, neg=neg)
    
    return res

  def to_sympy(self):
    if self.neg:
      return sympy.Mul(*list(map(lambda i: i.to_sympy(), self.args)), -1)
    else:
      return sympy.Mul(*list(map(lambda i: i.to_sympy(), self.args)))

  def to_latex(self, assoc=0):
    # separate numerator and denominator
    num = []
    den = []
    for i in self.args:
      if isinstance(i.unfold(), Pow) and i.unfold().args[1].is_neg:
        den += [i.invert()]
      else:
        num += [i]

    # convert numerator
    num_contents = ""
    if len(den) == 0 and len(num) == 1:
      num_contents = num[0].to_latex(0)
    elif len(den) != 0 and len(num) == 0:
      num_contents
    else:
      for i in num:
        if isinstance(i.unfold(), Number) and num_contents != "":
          num_contents += " \\cdot " + i.to_latex(10)
        else:
          num_contents += " " + i.to_latex(10)

    # convert denominator
    den_contents = ""
    for i in den:
      if isinstance(i.unfold(), Number) and den_contents != "":
        den_contents += " \\cdot " + i.to_latex(10)
      else:
        den_contents += " " + i.to_latex(10)

    if len(den) == 0:
      res = num_contents
    else:
      res = "\\frac{" + num_contents + "}{" + den_contents + "}"

    if assoc > 10:
      res = "\\left(" + res + "\\right)"

    return res

class Pow(AstNode):
  def __init__(self, base, exponent):
    super().__init__(base, exponent)

  def invert(self):
    return Pow(self.args[0], Mul(self.args[1], Number(-1))).flatten()

  def to_sympy(self):
    return sympy.Pow(*list(map(lambda i: i.to_sympy(), self.args)))

  def to_latex(self, assoc=0):
    # handle explicit inversion
    if isinstance(self.args[1].unfold(), Number) and self.args[1].n == -1:
      return "\\frac{1}{" + self.args[0].to_latex() + "}"
    elif self.args[1].unfold().is_neg:
      return "\\frac{1}{" + self.invert().to_latex() + "}"
    else:
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
    return sympy.log(self.args[0].to_sympy(), sympy.E)
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
  def invert(self):
    return Highlight(self.args[0].invert())
  def srepr(self):
    return self.args[0].srepr()
  def to_sympy(self):
    return self.args[0].to_sympy()
  def to_latex(self, assoc=0):
    return "\\textcolor{red}{" + self.args[0].to_latex(assoc) + "}"

