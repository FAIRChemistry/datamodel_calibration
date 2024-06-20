import logging

import numpy as np
import sympy as sp
from lmfit import Model as LMFitModel
from lmfit import Parameters
from lmfit.model import ModelResult
from scipy.optimize import root_scalar

from calipytion.core.calibrationmodel import CalibrationModel
from calipytion.core.fitstatistics import FitStatistics
from calipytion.core.parameter import Parameter

LOOGGER = logging.getLogger(__name__)


class CalModel:
    signal_var = "SIGNAL_PLACEHOLDER"

    def __init__(self, equation: str, dep_var: str, params: list[Parameter]):
        self.equation = equation
        self.params = params
        self.dep_var = dep_var
        self.indep_vars = [param.symbol for param in params if param.symbol != dep_var]
        self.model_callable = self._get_model_callable()
        self.lmfit_model: LMFitModel = self._prepare_model()
        self.lmfit_params: Parameters = self._prepare_params()
        self.lmfit_result: ModelResult | None = None

    @classmethod
    def from_calibration_model(cls, calibration_model: CalibrationModel):
        return cls(
            equation=calibration_model.signal_law,
            dep_var=calibration_model.molecule_symbol,
            params=calibration_model.parameters,
        )

    def _get_model_callable(self) -> callable:
        sp_expression = sp.sympify(self.equation)
        variables = [self.dep_var] + self.indep_vars
        return sp.lambdify(variables, sp_expression)

    def _prepare_model(self) -> LMFitModel:
        callable_ = self.model_callable

        return LMFitModel(callable_)

    def _get_param_dict(self, dep_var_values: np.ndarray):
        values_dict = self.lmfit_params.valuesdict()
        print(self.lmfit_params["a"])
        values_dict[self.dep_var] = dep_var_values

        return values_dict

    def _prepare_params(self):
        lm_params = Parameters()
        for param in self.params:
            lm_params.add(
                param.symbol,
                value=param.init_value,
                min=param.lower_bound,
                max=param.upper_bound,
            )

        return lm_params

    def fit(self, y: np.ndarray, x: np.ndarray, dep_var_name: str) -> LMFitModel:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        dep_var = {dep_var_name: x}

        self.lmfit_result = self.lmfit_model.fit(
            data=y,
            **dep_var,
            params=self.lmfit_params,
        )

        self.lmfit_params = self.lmfit_result.params

        self.update_result_params()

        return self.extract_fit_statistics(self.lmfit_result)

    def _get_root_eq(self):
        eq = self.equation + " - " + self.signal_var
        variables = [self.dep_var] + self.indep_vars + [self.signal_var]
        return sp.lambdify(variables, eq)

    def update_result_params(
        self,
    ) -> None:
        """
        Extract parameters from a lmfit result.
        and update the parameters list.
        """

        for name, lmf_param in self.lmfit_params.items():
            for param in self.params:
                if param.symbol == name:
                    param.value = lmf_param.value
                    param.stderr = lmf_param.stderr

    def calculate_roots(
        self, y: np.ndarray, lower_bond: float, upper_bond: float, extrapolate: bool
    ) -> np.ndarray:
        """
        Calculate the roots of the model equation within a given interval.
        """

        root_eq = self._get_root_eq()
        params = [{param.symbol: param.value for param in self.params}] * len(y)
        params = [
            {**param, self.signal_var: signal} for param, signal in zip(params, y)
        ]
        bracket = [lower_bond, upper_bond]

        roots = []
        failed_signals = []
        for param in params:
            try:
                root = root_scalar(root_eq, bracket=bracket, args=tuple(param.values()))
                roots.append(root.root)
            except ValueError:
                roots.append(np.nan)
                failed_signals.append(param[self.signal_var])

        if extrapolate and failed_signals:
            LOGGER.warning(
                f"Could not find roots for signals: {failed_signals} "
                f"in extended calibration range."
            )

        return np.array(roots)

    def extract_fit_statistics(self, lmfit_result: ModelResult) -> dict[str, float]:
        """
        Extract fit statistics from a lmfit result.
        """

        return FitStatistics(
            aic=lmfit_result.aic,
            bic=lmfit_result.bic,
            r2=lmfit_result.rsquared,
            rmsd=calculate_rmsd(lmfit_result.residual),
        )


def calculate_rmsd(residuals: np.ndarray) -> float:
    """Calculates root mean square deviation between measurements and fitted model."""
    residuals = np.array(residuals)
    return float(np.sqrt(sum(residuals**2) / len(residuals)))
