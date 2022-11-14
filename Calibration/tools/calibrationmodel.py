from typing import Dict, Optional, Callable
from lmfit import Model, Parameters
from lmfit.model import ModelResult
from scipy.optimize import curve_fit

from numpy import exp, ndarray


class CalibrationModel:
    def __init__(
        self,
        name: str,
        equation: Callable,
        parameters: Dict[str, float]
        ):
        self.name = name
        self.equation = equation
        self.parameters = parameters


    def fit(self, absorption: ndarray, concentration: ndarray) -> ModelResult:
        # Get parameter estimates
        result = curve_fit(
            f=self.equation, xdata=concentration, ydata=absorption)[0]
        self.parameters = dict(zip(self.parameters.keys(), result))

        # Initialize lmfit
        lmfit_model = Model(self.equation)
        lmfit_params = lmfit_model.make_params(**self.parameters)

        # Fit data to model
        self.result = lmfit_model.fit(
            data=absorption, x=concentration, params=lmfit_params)


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
