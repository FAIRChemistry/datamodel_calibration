from typing import Dict, Optional, Callable
from lmfit import Model, Parameters


class CalibrationModel:
    def __init__(
        self,
        name: str,
        equation: Callable,
        parameters: Optional[Dict[str, float]] = None,
        lmfit_model: Optional[Model] = None,
        lmfit_params: Optional[Parameters] = None):

        self.name = name
        self.equation = equation
        self.parameters = parameters
        self.lmfit_model = lmfit_model
        self.lmfit_params = lmfit_params

    def set_lmfit_parameters(self) -> Parameters:
        return self.lmfit_model.make_params(**self.parameters)


def linear1(x, a) -> float:
    return a*x


def quadratic(x, a, b) -> float:
    return a*x**2 + b*x


def poly3(x, a, b, c) -> float:
    return a*x**3 + b*x**2 + c*x


def poly_e(x, a, b) -> float:
    return a*exp(x/b)


def rational(x, a, b) -> float:
    return (a*x)/(b+x)
