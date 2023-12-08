import sdRDM

import copy
import numpy as np
import sympy as sp
import math
from typing import Dict, List, Optional, Tuple
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from lmfit import Model as LmfitModel
from lmfit.model import ModelResult
from .fitstatistics import FitStatistics
from .calibrationrange import CalibrationRange
from .parameter import Parameter


@forge_signature
class CalibrationModel(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibrationmodelINDEX"),
        xml="@id",
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the calibration model",
    )

    equation: Optional[str] = Field(
        default=None,
        description="Equation of the calibration model",
    )

    parameters: List[Parameter] = Field(
        description="Parameters of the calibration model equation",
        default_factory=ListPlus,
        multiple=True,
    )

    was_fitted: Optional[bool] = Field(
        default=None,
        description="Indicates if the model was fitted to the data",
    )

    calibration_range: Optional[CalibrationRange] = Field(
        description=(
            "Concentration and signal bounds in which the calibration model is valid."
        ),
        default_factory=CalibrationRange,
    )

    statistics: Optional[FitStatistics] = Field(
        description="Fit statistics of the calibration model",
        default_factory=FitStatistics,
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="9d6569843d37a52b2ab26af6e3ee12dea54192db"
    )

    def add_to_parameters(
        self,
        name: Optional[str] = None,
        value: Optional[float] = None,
        init_value: Optional[float] = None,
        standard_error: Optional[float] = None,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Parameter' to attribute parameters

        Args:
            id (str): Unique identifier of the 'Parameter' object. Defaults to 'None'.
            name (): Name of the parameter. Defaults to None
            value (): Value of the parameter. Defaults to None
            init_value (): Initial value of the parameter. Defaults to None
            standard_error (): Standard error of the parameter. Defaults to None
            lower_bound (): Lower bound of the parameter. Defaults to None
            upper_bound (): Upper bound of the parameter. Defaults to None
        """
        params = {
            "name": name,
            "value": value,
            "init_value": init_value,
            "standard_error": standard_error,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        }
        if id is not None:
            params["id"] = id
        self.parameters.append(Parameter(**params))
        return self.parameters[-1]

    def fit(
        self,
        concentrations: List[float],
        signals: List[float],
        init_param_value: float = 0.1,
    ):
        # define calibration bounds for the model
        self.calibration_range = CalibrationRange(
            conc_lower=min(concentrations),
            conc_upper=max(concentrations),
            signal_lower=min(signals),
            signal_upper=max(signals),
        )

        # arrayify input
        if not isinstance(concentrations, np.ndarray):
            concentrations = np.array(concentrations)

        if not isinstance(signals, np.ndarray):
            signals = np.array(signals)

        _callable, variables = self._get_model_callable(
            solve_for="signal",
            dependent_variable="concentration",
        )

        # initialize lmfit model
        lmfit_model = LmfitModel(_callable, name=self.equation)

        # initialize parameter dict
        parameters = dict(zip(variables, [init_param_value] * len(variables)))
        parameters["concentration"] = concentrations

        lmfit_result = lmfit_model.fit(data=signals, **parameters, nan_policy="omit")

        # extract fit statistics
        self.was_fitted = lmfit_result.success
        self._extract_parameters(lmfit_result)
        self._extract_lmfit_statistics(lmfit_result)

        return lmfit_result

    def calculate(
        self,
        signals: List[float],
        allow_extrapolation: bool = False,
    ) -> List[float]:
        if not self.was_fitted:
            raise ValueError(
                "Model was not fitted to calibration data. Fit model first"
            )

        if not isinstance(signals, np.ndarray):
            signals = np.array(signals)

        # get root equation
        equality = self._get_equality()
        root_eq = equality.lhs - equality.rhs

        roots = []
        params = copy.copy(self._params)

        for signal in signals:
            if math.isnan(signal):
                roots.append([float("nan")])
                continue

            params[equality.rhs] = signal

            # calculate all possible real roots for equation
            roots.append(list(sp.roots(sp.real_root(root_eq.subs(params))).keys()))

        # reshape results, fill nan columns for signals above upper calibration range
        matrix = (
            np.zeros([len(roots), len(max(roots, key=lambda x: len(roots)))]) * np.nan
        )

        # replace complex solutions with nans
        for i, j in enumerate(roots):
            without_complex = [
                float("nan") if isinstance(value, sp.core.add.Add) else value
                for value in j
            ]

            matrix[i][0 : len(without_complex)] = without_complex

        roots = np.array(matrix).T

        # get root alternative with most values within calibration bonds
        n_values_in_calibration_range = []
        for result in roots:
            n_values_in_calibration_range.append(
                (
                    (self.calibration_range.conc_lower < result)
                    & (result < self.calibration_range.conc_upper)
                ).sum()
            )

        correct_roots = roots[np.nanargmax(n_values_in_calibration_range)]

        if not allow_extrapolation:
            correct_roots[
                (self.calibration_range.conc_lower > correct_roots)
                | (self.calibration_range.conc_upper < correct_roots)
            ] = float("nan")

        return correct_roots.tolist()

    def _get_model_callable(
        self,
        solve_for: str,
        dependent_variable: str,
    ) -> Tuple[callable, List[str]]:
        """Converts the equation string to a callable function.

        Args:
            solve_for (str): Independent variable to solve for
            dependent_variable (str): Dependent variable

        Returns:
            callable: Callable function based on the model string
        """

        equality = self._get_equality()
        equality = sp.solve(equality, solve_for)[0]
        variables = [str(x) for x in list(equality.free_symbols)]
        variables.insert(
            0, variables.pop(variables.index(dependent_variable))
        )  # dependent variable needs to be in first pos for lmfit --> change of variable order

        _callable = sp.lambdify(variables, equality)

        return _callable, variables

    def _get_equality(self) -> sp.Equality:
        """Converts the equation string to a sympy equality.

        Returns:
            sp.Equality: Sympy equality
        """

        lhs, rhs = self.equation.split("=")
        equality = sp.Equality(sp.sympify(lhs), sp.sympify(rhs))

        return equality

    def _extract_lmfit_statistics(self, lmfit_result: ModelResult):
        statistics = FitStatistics(
            aic=lmfit_result.aic,
            bic=lmfit_result.bic,
            r2=lmfit_result.rsquared,
            rmsd=self._calculate_rmsd(lmfit_result.residual),
        )

        self.statistics = statistics

    def _calculate_rmsd(self, residuals: np.ndarray) -> float:
        """Calculates root mean square deviation between measurements and fitted model."""
        residuals = np.array(residuals)
        return float(np.sqrt(sum(residuals**2) / len(residuals)))

    def _extract_parameters(
        self,
        lmfit_result: ModelResult,
    ):
        parameters = []
        for name, param in lmfit_result.params.items():
            parameters.append(
                Parameter(
                    name=name,
                    value=param.value,
                    init_value=param.init_value,
                    standard_error=param.stderr,
                    lower_bound=param.min,
                    upper_bound=param.max,
                )
            )

        self.parameters = parameters

    @property
    def _params(self) -> Dict[str, float]:
        return {param.name: param.value for param in self.parameters}

    @property
    def signal_callable(self):
        _callable, _ = self._get_model_callable(
            solve_for="signal",
            dependent_variable="concentration",
        )

        def function(concentration: List[float], **params):
            if not isinstance(concentration, np.ndarray):
                concentration = np.array(concentration)

            return _callable(concentration, **params)

        return function

    @property
    def concentration_callable(self):
        _callable, _ = self._get_model_callable(
            solve_for="concentration",
            dependent_variable="signal",
        )

        def function(signal: List[float], **params):
            if not isinstance(signal, np.ndarray):
                signal = np.array(signal)

            return _callable(signal, **params)

        return function

    def _get_residuals(
        self, concentrations: List[float], signals: List[float]
    ) -> np.ndarray:
        return np.array(signals) - self.signal_callable(concentrations, **self._params)
