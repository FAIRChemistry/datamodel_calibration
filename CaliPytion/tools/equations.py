from sympy import Symbol, exp, Equality

# define symbols 
a = Symbol("a")
b = Symbol("b")
c = Symbol("c")
concentration = Symbol("concentration")
signal = Symbol("signal")

# define calibration equations
linear = Equality((a*concentration), signal)
quadratic = Equality((a*concentration**2 + b*concentration), signal)
poly_3 = Equality((a*concentration**3 + b*concentration**2 + c*concentration), signal)
poly_e = Equality((a*exp(concentration/b)), signal)
rational = Equality(((a*concentration) / (b+concentration)), signal)