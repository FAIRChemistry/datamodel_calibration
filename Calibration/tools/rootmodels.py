from typing import Dict, Callable

import numpy as np
from scipy.optimize import fsolve


def root_linear1(x: float, params: Dict[str, float]) -> float:
    a, absorption = params.values()
    return a*x - absorption


def root_quadratic(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return a*x**2 + b*x - absorption


def root_poly3(x: float, params: Dict[str, float]) -> float:
    a, b, c, absorption = params.values()
    return a*x**3 + b*x**2 + c*x - absorption


def root_poly_e(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return a*np.exp(x/b) - absorption


def root_rational(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return (a*x)/(b+x) - absorption

# Mapper for equations from CalibrationModel
equation_dict: Dict[str, Callable] = {
    "Linear": root_linear1,
    "Quadratic": root_quadratic,
    "3rd polynominal": root_poly3,
    "Exponential": root_poly_e,
    "Rational": root_rational
    }


# TODO legacy code? -->>
def to_concentration(
    standard_curve: StandardCurve,
    data: np.ndarray, 
    standard_curve_model_name: str= None, 
    allow_extrapolation:bool = False,
    ) -> np.ndarray:

    """Converts absobrance / peak area into concentration based on StandardCurve.

    Args:
        standard_curve (StandardCurve): StandardCurve object, containing model for 
        concentration calculation.

        data (ndarray): Measured peak area / absorbance

        standard_curve_model (str, optional): Optionally, a differing model from the best model 
        from StandardCurve can be provided by passing the name of the respective model. Defaults to "".

    Returns:
        ndarray: Calculated concentrations
    """



    if isinstance(data, np.ndarray):
        shape = data.shape
        data = data.flatten()
        result = np.zeros(data.shape)

    else:
        result = []

    if standard_curve_model_name is not None:
        model = standard_curve.model_dict[standard_curve_model_name]
    else:
        model = standard_curve.model

    equation: Callable = equation_dict[model.name]
    params: dict = model.result.params.valuesdict()

    for value in range(len(data)):
        params["absorption"] = data[value]

        if isinstance(data, np.ndarray):
            result[value] = fsolve(equation, 0, params)
        else:
            result.append(fsolve(equation, 0, params))

    if isinstance(data, np.ndarray):
        result = result.reshape(shape)
        max_conc = max(standard_curve.concentration)
        result[result > max_conc] = np.nan

    # Check calibration bounds: 
    if max(data) > max(standard_curve.absorption):
        calibration_bound = max(standard_curve.absorption)
        count = (data > calibration_bound).sum()
        print(f"ExtrapolationWarning!\n{count} entries in data are greater than upper calibration bound of {calibration_bound}!")

    return result


if __name__ == "__main__":
    from pyenzymekinetics.parameterestimator.helper.load_utitlity import absorbance_measured, calibration_abso, calibration_conc
    calibration = StandardCurve(calibration_conc, calibration_abso, "mM", "TestSubstance")

    result = to_concentration(calibration, absorbance_measured)
    print(result.shape)
    