from typing import Callable, Tuple
from lmfit import Model
import sympy as s
from sympy import Equality, lambdify, solve
import numpy as np


class CalibrationModel:
    """Class handling the fitting and statistics calculation of a calibration model."""

    def __init__(self, name: str, equation: Equality):
        self.name = name
        self.equation = equation
        self.equation_string = self._equation_to_string(equation)

        self.aic: float = None
        self.bic: float = None
        self.r_squared: float = None
        self.residuals = None
        self.best_fit = None
        self.params: dict = None
        self.rmsd = None
        self._lmfit_result = None

    def _fit(self, concentrations: np.ndarray, signals: np.ndarray):
        """Fits a kinetic model

        Args:
            concentrations (np.ndarray): _description_
            signals (np.ndarray): _description_
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
        self.r_squared = result.rsquared
        self.residuals = result.residual
        self.best_fit = result.best_fit
        self.params = result.params.valuesdict()
        self.rmsd = self._calculate_rmsd(self.residuals)
        self._lmfit_result = result

    def _calculate_rmsd(self, residuals: np.ndarray) -> float:
        """Calculates root mean square deviation between measurements and fitted model."""
        return np.sqrt(sum(residuals**2) / len(residuals))

    def calculate_roots(
        self,
        signals: list,
        allow_extrapolation: bool = False,
    ):
        """Calculates all roots for a model and returns the roots within calibration bonds"""
        calibration_conc_range = self._lmfit_result.userkws["concentration"]
        min_concentration = min(calibration_conc_range)
        max_concentration = max(calibration_conc_range)

        root_eq = self.equation.lhs - self.equation.rhs

        results = []
        parameters = self.params.copy()
        for signal_value in signals:
            if not np.isnan(signal_value):

                parameters[self.equation.rhs] = signal_value

                results.append(
                    list(s.roots(s.real_root(root_eq.subs(parameters))).keys())
                )
            else:

                results.append([float("nan")])

        # reshape results, fill nan columns for signals above upper calibration range
        matrix = np.zeros(
            [len(results), len(max(results, key=lambda x: len(results)))]) * np.nan

        # replace complex solutions with nans
        for i, j in enumerate(results):
            without_complex = [float("nan") if isinstance(value, s.core.add.Add)
                               else value for value in j]

            matrix[i][0: len(without_complex)] = without_complex

        results = np.array(matrix).T

        # get root alternative with most values within calibration bonds
        n_values_in_calibration_range = []
        for result in results:
            n_values_in_calibration_range.append(
                ((min_concentration < result) & (result < max_concentration)).sum()
            )

        correct_roots = results[np.nanargmax(n_values_in_calibration_range)]

        if not allow_extrapolation:
            correct_roots[(min_concentration > correct_roots) |
                          (max_concentration < correct_roots)] = float("nan")

        return correct_roots

    def calculate_concentration(
        self, signal: float | np.ndarray, allow_extrapolation: bool = False
    ) -> float | np.ndarray:
        """Calculates unknown concentrations based on fit of Calibration model.

        Args:
            signals (float | np.ndarray): Measured signals of unknown concentration
            allow_extrapolation (bool): Allow or disallow extrapolation for 
            concentration calculation. Defaults to False.

        Returns:
            float | np.ndarray: Calculated concentration.
        """

        # Concert input to numpy array
        calibration_signals = self._lmfit_result.data
        min_signals = min(calibration_signals)
        max_signals = max(calibration_signals)

        # replace values above upper calibration limit with nans
        if not allow_extrapolation:
            extrapolation_pos = np.where(signal > max_signals)[0]
            if extrapolation_pos.size != 0:
                print(
                    f"{len(extrapolation_pos)} measurements are above upper calibration limit of "
                    f"{max(calibration_signals):.2f}. Respective measurments are replaced with "
                    f"nans. To extrapolate, set 'allow_extrapolation = True'"
                )
                print(f"extrapolation_pos: {extrapolation_pos}")

                signal[extrapolation_pos] = np.nan

        # convert equation to solve for concentration
        functions = self._get_np_function(
            self.equation, solve_for="concentration", dependent_variable="signal")

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
        equation: Equality, solve_for: str, dependent_variable: str
    ) -> Tuple[Callable, list]:
        equation: Equality = solve(equation, solve_for)[0]

        variables = [str(x) for x in list(equation.free_symbols)]
        variables.insert(
            0, variables.pop(variables.index(dependent_variable))
        )  # dependent variable needs to be in first pos for lmfit --> change of variable order
        return (lambdify(variables, equation), variables)

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
