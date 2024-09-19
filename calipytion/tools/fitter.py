import logging
from typing import Callable

import numpy as np
import sympy as sp
from lmfit import Model as LMFitModel
from lmfit import Parameters
from lmfit.model import ModelResult
from scipy.optimize import root_scalar

from calipytion.model import CalibrationModel, FitStatistics, Parameter
from calipytion.tools.utility import calculate_rmsd

LOGGER = logging.getLogger(__name__)


class Fitter:
    signal_var = "SIGNAL_PLACEHOLDER"

    def __init__(self, equation: str, indep_var: str, params: list[Parameter]):
        self.equation = equation
        self.params = params
        self.indep_var = indep_var
        self.dep_vars = [param.symbol for param in params if param.symbol != indep_var]
        self.model_callable = self._get_model_callable()
        self.lmfit_model: LMFitModel = self._prepare_model()
        self.lmfit_params: Parameters = self._prepare_params()
        self.lmfit_result: ModelResult | None = None

    def fit(self, y: np.ndarray, x: np.ndarray, indep_var_symbol: str) -> FitStatistics:
        if not isinstance(x, np.ndarray):
            x = np.array(x)
        if not isinstance(y, np.ndarray):
            y = np.array(y)

        kwargs = {indep_var_symbol: x}

        self.lmfit_result = self.lmfit_model.fit(
            data=y, params=self.lmfit_params, **kwargs
        )

        self.lmfit_params = self.lmfit_result.params

        self._update_result_params()

        return self.extract_fit_statistics(self.lmfit_result)

    def calculate_roots(
        self, y: np.ndarray, lower_bond: float, upper_bond: float, extrapolate: bool
    ) -> np.ndarray:
        """ "
        Calculate the roots of the equation for the given signals.

        Parameters
        ----------
        y : np.ndarray
            The signals for which the roots should be calculated.
        lower_bond : float
            The lower bond for the root search.
        upper_bond : float
            The upper bond for the root search.
        extrapolate : bool
            If True, the function will evaluate the equation for the given signals that are outside
            the bounds.

        Returns
        -------
        np.ndarray
            The roots of the equation for the given signals.

        Raises
        ------
        ValueError
            If a parameter has no value set.
        """

        root_eq = self._get_root_eq()

        for param in self.params:
            if param.value is None:
                raise ValueError(f"Parameter '{param.symbol}' has no value set.")

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

    @classmethod
    def from_calibration_model(cls, calibration_model: CalibrationModel):
        assert (
            calibration_model.signal_law is not None
        ), "Calibration model has no signal law."
        assert (
            calibration_model.molecule_id is not None
        ), "Calibration model has no molecule symbol."

        return cls(
            equation=calibration_model.signal_law,
            indep_var=calibration_model.molecule_id,
            params=calibration_model.parameters,
        )

    def _get_model_callable(self) -> Callable[..., float]:
        sp_expression = sp.sympify(self.equation)
        variables = [self.indep_var] + self.dep_vars

        return sp.lambdify(variables, sp_expression)

    def _prepare_model(self) -> LMFitModel:
        callable_ = self.model_callable

        model = LMFitModel(callable_, independent_vars=[self.indep_var])

        return model

    def _get_param_dict(self, indep_var_values: np.ndarray):
        values_dict = self.lmfit_params.valuesdict()
        values_dict[self.indep_var] = indep_var_values

        return values_dict

    def _prepare_params(self):
        lm_params = Parameters()
        for param in self.params:
            lm_params.add(
                param.symbol,
                value=param.init_value,
                min=param.lower_bound if param.lower_bound is not None else -np.inf,
                max=param.upper_bound if param.upper_bound is not None else np.inf,
            )

        return lm_params

    def _get_root_eq(self):
        eq = self.equation + " - " + self.signal_var
        variables = [self.indep_var] + self.dep_vars + [self.signal_var]
        return sp.lambdify(variables, eq)

    def _update_result_params(
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

    def extract_fit_statistics(self, lmfit_result: ModelResult) -> FitStatistics:
        """
        Extract fit statistics from a lmfit result.
        """

        assert self.lmfit_model is not None, "Model was not fitted."

        if lmfit_result.success:
            rmsd = calculate_rmsd(lmfit_result.residual)

            return FitStatistics(
                aic=lmfit_result.aic,  # type: ignore
                bic=lmfit_result.bic,  # type: ignore
                r2=lmfit_result.rsquared,
                rmsd=rmsd,
            )

        raise ValueError("Model did not converge.")


if __name__ == "__main__":
    import numpy as np

    from calipytion.model import Parameter

    params = []
    params.append(
        Parameter(
            symbol="a",
            init_value=1.0,
            lower_bound=-1,
            upper_bound=1e6,
        )
    )
    params.append(
        Parameter(
            symbol="b",
            init_value=1.0,
            lower_bound=-1,
            upper_bound=1e6,
        )
    )

    equation = "a * Meth + b"

    model = Fitter(
        equation=equation,
        indep_var="Meth",
        params=params,
    )

    print(model.indep_var)
    print(model.equation)
    print(model.lmfit_params)

    x = [0, 2, 4, 6]
    y = [1, 2, 3, 4]

    res = model.fit(y, x, "Meth")
