from typing import Callable, Tuple
from lmfit import Model
from sympy import Equality, lambdify, solve
from numpy import ndarray, array, sum, sqrt, where, nan

from CaliPytion.tools.equations import *


class CalibrationModel:
    def __init__(
        self,
        name: str,
        equation: Equality
        ):

        self.name = name
        self.equation = equation
        self.equation_string = self._equation_to_string(equation)
        

    def _fit(self, concentrations: ndarray, signals: ndarray):
        """Fits a kinetic model 

        Args:
            concentrations (ndarray): _description_
            signals (ndarray): _description_
        """

        # define lmfit model from sympy equation
        model = self.equation
        function, parameter_keys = self._get_np_function(model, solve_for="signal", dependent_variable="concentration")
        lmfit_model = Model(function, name=self.equation_string)

        # initialize parameters
        parameters = dict(zip(parameter_keys, [0.1]*len(parameter_keys)))
        parameters["concentration"] = concentrations

        # fit data to model
        result = lmfit_model.fit(data=signals, **parameters)

        # extract fit statistics
        self.aic = result.aic
        self.bic = result.bic
        self.r2 = result.rsquared
        self.residuals = result.residual
        self.best_fit = result.best_fit
        self.params = result.params.valuesdict()
        self.rmsd = self._calculate_RMSD(self.residuals)
        self._lmfit_result = result


    def _calculate_RMSD(self, residuals: ndarray) -> float:
        return sqrt(sum(residuals**2) / len(residuals))
    
    
    def calculate_concentration(self, 
                                signal: float | ndarray, 
                                allow_extrapolation: bool = False
                                ) -> float | ndarray:
        """Calculates unknown concentrations based on fit of Calibration model.

        Args:
            signal (float | np.ndarray): Measured signal(s) of unknown concentration
            allow_extrapolation (bool): Allow or disallow extrapolation for concentration calculation. Defaults to False.

        Returns:
            float | np.ndarray: Calculated concentration.
        """

        # Concert input to numpy array
        signal = array(signal).astype("float")
        calibration_signals = self._lmfit_result.data

        # replace values above upper calibration limit with nans
        if not allow_extrapolation:
            extrapolation_pos = where(signal > max(calibration_signals))[0]
            if extrapolation_pos.size != 0:
                print(f"{len(extrapolation_pos)} measurements are above upper calibration limit of {max(calibration_signals):.2f}.\n \
                      Respective measurments are replaced with nans. To extrapolate, set 'allow_extrapolation = True'")
                signal[extrapolation_pos] = nan

        # convert equation to solve for concentration
        function, _ = self._get_np_function(self.equation, solve_for="concentration", dependent_variable="signal")

        # set parameters
        parameters = self.params.copy()
        parameters["signal"] = signal

        result = function(**parameters)

        return result


    @staticmethod 
    def _get_np_function(equation: Equality, solve_for: str, dependent_variable: str) -> Tuple[Callable, list]:
        equation: Equality = solve(equation, solve_for)[0]
        variables = [str(x) for x in list(equation.free_symbols)]
        variables.insert(0, variables.pop(variables.index(dependent_variable))) # dependent variable needs to be in first pos for lmfit --> change of variable order
        return (lambdify(variables, equation), variables)
        
    def visualize_fit(self, **kwargs):
        self._lmfit_result.plot_fit(**kwargs)

    def visualize_residuals(self, **kwargs):
        self._lmfit_result.plot_residuals(**kwargs)

    @staticmethod
    def _equation_to_string(equation: Equality) -> str:
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

        
if __name__ == "__main__":
    from sdRDM import DataModel

    dm, lib = DataModel.parse(path="rational_test.xml")

    print(dm)