from lmfit import Model
from lmfit.model import ModelResult
from sympy import Equality, lambdify, solve
from numpy import ndarray, array, sum, sqrt, where, nan

from CaliPytion.tools.equations import *


class CalibrationModel:
    def __init__(
        self,
        name: str,
        equation: Equality,
        ):
        self.name = name
        self.equation = equation
        self.initial_params = self._initialze_params()
        print("pause")


    def _initialze_params(self) -> dict:
        """Initializes parameters from Sympy equation. Initializes all parameters with 0.

        Returns:
            dict: Key value pairs of all model parameters
        """
        param_list = [str(x) for x in list(self.equation.lhs.free_symbols)]
        return dict(zip(param_list, [0]*len(param_list)))

    def fit(self, concentrations: ndarray, signals: ndarray):

        # define lmfit model from sympy equation
        model = self.equation.lhs
        variables = [str(x) for x in list(model.free_symbols)]
        variables.insert(0, variables.pop(variables.index("concentration"))) # dependent variable needs to be in first pos for lmfit --> change of variable order
        model_func = lambdify(variables, model)
        lm_mod = Model(model_func, name=equation_to_string(self.equation))

        # set parameters
        params = self.initial_params
        params["concentration"] = concentrations

        # fit data to model
        result = lm_mod.fit(data=signals, **params, nan_policy="omit")

        # extract fit statistics
        self.aic = result.aic
        self.bic = result.bic
        self.r2 = result.rsquared
        self.residuals = result.residual
        self.best_fit = result.best_fit
        self.params = result.params.valuesdict()
        self.rmsd = self.calculate_RMSD(self.residuals)
        self.lmfit_result = result

    def calculate_RMSD(self, residuals: ndarray) -> float:
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

        signal = array(signal).astype("float")
        calibration_signals = self.lmfit_result.data

        # replace values above upper calibration limit with nans
        if not allow_extrapolation:
            extrapolation_pos = where(signal > max(calibration_signals))[0]
            if extrapolation_pos.size != 0:
                print(f"{len(extrapolation_pos)} measurements are above upper calibration limit of {max(calibration_signals):.2f}.\n \
                      Respective measurments are replaced with nans. To extrapolate set 'allow_extrapolation' = True")
                signal[extrapolation_pos] = nan

        # convert equation to solve for concentration
        equation: Equality = solve(self.equation, "concentration")[0]
        function = lambdify(list(equation.free_symbols), equation)

        # set parameters
        params = self.params
        params["signal"] = signal

        result: ndarray = function(**params)

        if result.size > 1:
            return result
        else:
            return float(result)
        
    def visualize_fit(self, **kwargs):
        self.lmfit_result.plot_fit(**kwargs)

    def visualize_residuals(self, **kwargs):
        self.lmfit_result.plot_residuals(**kwargs)

        
if __name__ == "__main__":
    import numpy as np
    from CaliPytion.tools.equations import linear
    import matplotlib.pyplot as plt
    conc = np.linspace(0,10,10)
    sig = np.linspace(0,20,10)



    mod = CalibrationModel(name=("linear"), equation=linear)
    mod.fit(conc,sig)
    print(mod.r2)
    mod.visualize_fit()
    plt.show