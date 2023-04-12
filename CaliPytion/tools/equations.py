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
poly_e = Equality((a*concentration*exp(concentration/b)), signal)
rational = Equality((a*concentration / b*concentration), signal)


def equation_to_string(equation: Equality) -> str:
    """Formats the string representation of a sympy.Equality object.

    Args:
        equation (Equality): Sympy Equality.

    Returns:
        str: "left_side = right_side"
    """
    equation = str(equation)

    left_side, right_side = equation.split(", ")
    left_side = left_side.split("Eq(")[1]

    right_side = right_side[:-1]

    return f"{right_side} = {left_side}"