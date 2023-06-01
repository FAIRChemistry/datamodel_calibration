from typing import Callable, Tuple, Dict
from lmfit import Model
import sympy as s
from sympy import Equality, lambdify, solve, pprint
import numpy as np
from numpy import ndarray, array, sum, sqrt, where, nan

from CaliPytion.tools.equations import *


class CalibrationModel:
    def __init__(self, name: str, equation: Equality):
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
        function, parameter_keys = self._get_np_function(
            model, solve_for="signal", dependent_variable="concentration"
        )
        lmfit_model = Model(function, name=self.equation_string)

        # initialize parameters
        parameters = dict(zip(parameter_keys, [0.1] * len(parameter_keys)))
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

    def calculate_roots(
        self,
        signals: list,
        allow_extrapolation: bool = False,
    ):
        calibration_signals = self._lmfit_result.data
        min_signals = min(calibration_signals)
        max_signals = max(calibration_signals)

        print(f"signals: {signals}")
        print(f"type of signals: {type(signals)}")
        print(f"type of signals entry: {type(signals[0])}")

        # replace values above upper calibration limit with nans
        if not allow_extrapolation:
            extrapolation_pos = where(signals > max_signals)[0]
            if extrapolation_pos.size != 0:
                print(
                    f"{len(extrapolation_pos)} measurements are above upper calibration limit of {max(calibration_signals):.2f}.\n \
                      Respective measurments are replaced with nans. To extrapolate, set 'allow_extrapolation = True'"
                )
                print(f"extrapolation_pos: {extrapolation_pos}")
                print(type(extrapolation_pos[0]))

                print(f"pos_array {extrapolation_pos}")
                extrapolation_pos = extrapolation_pos.astype(int)
                print(f"pos_array type {type(extrapolation_pos[0])}")

                signals[extrapolation_pos] = np.nan

        print(f"signals after correction: {signals}")

        root_eq = self.equation.lhs - self.equation.rhs

        results = []
        parameters = self.params.copy()
        for signal in signals:
            if not np.isnan(signal):
                print(f"signal: {signal}")
                parameters[self.equation.rhs] = signal
                results.append(
                    list(s.roots(s.real_root(root_eq.subs(parameters))).keys())
                )
            else:
                results.append([np.nan])

        # reshape results, fill nan columns for signals above upper calibration range
        matrix = np.zeros([len(results), len(max(results, key=lambda x: len(results)))])
        for i, j in enumerate(results):
            matrix[i][0 : len(j)] = j

        results = np.array(matrix).T
        print(results)

        n_values_in_calibration_range = []
        for result in results:
            n_values_in_calibration_range.append(
                ((min_signals < result) & (result < max_signals)).sum()
            )

        correct_roots = results[np.argmax(n_values_in_calibration_range)]

        return correct_roots

    def calculate_concentration(
        self, signal: float | ndarray, allow_extrapolation: bool = False
    ) -> float | ndarray:
        """Calculates unknown concentrations based on fit of Calibration model.

        Args:
            signal (float | np.ndarray): Measured signal(s) of unknown concentration
            allow_extrapolation (bool): Allow or disallow extrapolation for concentration calculation. Defaults to False.

        Returns:
            float | np.ndarray: Calculated concentration.
        """

        # Concert input to numpy array
        calibration_signals = self._lmfit_result.data
        min_signals = min(calibration_signals)
        max_signals = max(calibration_signals)

        # replace values above upper calibration limit with nans
        if not allow_extrapolation:
            extrapolation_pos = where(signal > max_signals)[0]
            if extrapolation_pos.size != 0:
                print(
                    f"{len(extrapolation_pos)} measurements are above upper calibration limit of {max(calibration_signals):.2f}.\n \
                      Respective measurments are replaced with nans. To extrapolate, set 'allow_extrapolation = True'"
                )
                print(f"extrapolation_pos: {extrapolation_pos}")

                signal[extrapolation_pos] = nan

        # convert equation to solve for concentration
        functions = self._get_np_functions(
            self.equation, solve_for="concentration", dependent_variable="signal"
        )

        # set parameters
        parameters = self.params.copy()
        parameters["signal"] = signal

        solutions = []
        for function in functions:
            solutions.append(function[0](**parameters))

        n_values_in_calibration_range = []
        for solution in solutions:
            n_values_in_calibration_range.append(
                ((min_signals < solution) & (solution < max_signals)).sum()
            )

        return solutions[np.argmax(n_values_in_calibration_range)]

    @staticmethod
    def _get_np_function(
        eq: Equality, solve_for: str, dependent_variable: str
    ) -> Tuple[Callable, list]:
        equation: Equality = solve(eq, solve_for)[0]

        variables = [str(x) for x in list(equation.free_symbols)]
        variables.insert(
            0, variables.pop(variables.index(dependent_variable))
        )  # dependent variable needs to be in first pos for lmfit --> change of variable order
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
