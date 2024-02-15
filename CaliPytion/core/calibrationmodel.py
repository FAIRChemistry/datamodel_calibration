import sdRDM

import numpy as np
import sympy as sp
from typing import List, Optional, Tuple
from pydantic import PrivateAttr
from uuid import uuid4
from pydantic_xml import attr, element, wrapped
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from lmfit import Model as LmfitModel
from lmfit.model import ModelResult
from .parameter import Parameter
from .calibrationrange import CalibrationRange
from .fitstatistics import FitStatistics


@forge_signature
class CalibrationModel(
    sdRDM.DataModel,
    nsmap={
        "": "https://github.com/FAIRChemistry/CaliPytion@0daea0e64ce2613de44d9c6c855c26093c755d38#CalibrationModel"
    },
):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    name: str = element(
        description="Name of the calibration model",
        tag="name",
        json_schema_extra=dict(),
    )

    signal_equation: str = element(
        description="Equation for the measured signal",
        tag="signal_equation",
        json_schema_extra=dict(),
    )

    parameters: List[Parameter] = wrapped(
        "parameters",
        element(
            description="Parameters of the calibration equation",
            default_factory=ListPlus,
            tag="Parameter",
            json_schema_extra=dict(multiple=True),
        ),
    )

    was_fitted: Optional[bool] = element(
        description="Indicates if the model was fitted to the data",
        default=False,
        tag="was_fitted",
        json_schema_extra=dict(),
    )

    calibration_range: Optional[CalibrationRange] = element(
        description=(
            "Concentration and signal bounds in which the calibration model is valid."
        ),
        default_factory=CalibrationRange,
        tag="calibration_range",
        json_schema_extra=dict(),
    )

    statistics: Optional[FitStatistics] = element(
        description="Fit statistics of the calibration model",
        default_factory=FitStatistics,
        tag="statistics",
        json_schema_extra=dict(),
    )
    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="0daea0e64ce2613de44d9c6c855c26093c755d38"
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
    ) -> Parameter:
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

    def add_parameter(
        self,
        name: Optional[str] = None,
        value: Optional[float] = None,
        init_value: Optional[float] = None,
        standard_error: Optional[float] = None,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        id: Optional[str] = None,
    ) -> Parameter:

        params = {
            "name": name,
            "value": value,
            "init_value": init_value,
            "standard_error": standard_error,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        }

        if not self.parameters:
            self.parameters.append(Parameter(**params))
            return self.parameters[-1]

        else:
            if name in [p.name for p in self.parameters]:
                param = self.get_parameter(name)
                param.value = value
                param.init_value = init_value
                param.standard_error = standard_error
                param.lower_bound = lower_bound
                param.upper_bound = upper_bound
                return param
            else:
                self.parameters.append(Parameter(**params))
                return self.parameters[-1]

    def _create_parameters(self, species_id: str):
        for symbol in self._symbols_list:
            if symbol != species_id:
                self.add_parameter(name=symbol, init_value=0.1)

    def get_parameter(self, name: str) -> Parameter:
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def fit(
        self,
        concentrations: List[float],
        signals: List[float],
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

        _callable, variables = self.signal_callable

        # initialize lmfit model
        lmfit_model = LmfitModel(_callable, name=self.name)

        # initialize parameter dict
        parameters = self.init_param_dict
        parameters[self.species_id] = concentrations

        lmfit_result = lmfit_model.fit(data=signals, **parameters, nan_policy="omit")

        # extract fit statistics
        self.was_fitted = lmfit_result.success
        self._extract_parameters(lmfit_result)
        self._extract_lmfit_statistics(lmfit_result)

        return lmfit_result

    def calculate_signals(self, concentrations: List[float]) -> List[float]:
        """
        Calculates the signals corresponding to a given list of concentrations using the fitted calibration model.

        Args:
            concentrations (List[float]): A list of concentration values for which signals need to be calculated.

        Returns:
            List[float]: A list of signals corresponding to the input list of concentrations.

        Raises:
            ValueError: If the model has not been fitted yet.
        """

        if not self.was_fitted:
            raise ValueError("The model has not been fitted yet.")

        concentrations = self._arrayify_input(concentrations)
        callable, _ = self.signal_callable

        return callable(concentrations, **self.param_dict).tolist()

    def calculate_concentrations(
        self, signals: List[float], extrapolate: bool = False
    ) -> List[float]:
        """
        Calculates the concentrations corresponding to a given list of signals using the calibration model.

        Args:
            signals (List[float]): A list of signal values for which concentrations need to be calculated.
            extrapolate (bool): A flag indicating whether to extrapolate concentrations for signals outside the calibration range. Defaults to False.

        Returns:
            List[float]: A list of concentrations corresponding to the input list of signals.

        Raises:
            ValueError: If the model has not been fitted yet.
        """
        if not self.was_fitted:
            raise ValueError("The model has not been fitted yet.")

        conc_eq_string = f"{self.signal_equation} - signal"
        conc_eq = sp.sympify(conc_eq_string)

        roots = []
        params = self.param_dict.copy()

        for signal in signals:
            if np.isnan(signal):
                roots.append([np.nan])
                continue

            params["signal"] = signal
            roots.append(list(sp.roots(sp.real_root(conc_eq.subs(params))).keys()))

        matrix = np.full((len(roots), len(max(roots, key=lambda x: len(x)))), np.nan)

        for i, root in enumerate(roots):
            without_complex = [
                float("nan") if isinstance(value, sp.core.add.Add) else value
                for value in root
            ]
            matrix[i, : len(without_complex)] = without_complex

        roots = np.array(matrix).T

        n_values_in_calibration_range = [
            (
                (self.calibration_range.conc_lower < result)
                & (result < self.calibration_range.conc_upper)
            ).sum()
            for result in roots
        ]

        correct_roots = roots[np.nanargmax(n_values_in_calibration_range)]

        if not extrapolate:
            correct_roots[
                (self.calibration_range.conc_lower > correct_roots)
                | (self.calibration_range.conc_upper < correct_roots)
            ] = float("nan")

        return correct_roots.tolist()

    def _arrayify_input(self, input: List[float]) -> np.ndarray:
        if not isinstance(input, np.ndarray):
            input = np.array(input)
        return input

    def _replace_equation_symbols(self, old: str, new: str):
        eq = self.signal_equation.replace(old, new)
        self.signal_equation = eq

    def _extract_parameters(
        self,
        lmfit_result: ModelResult,
    ):
        parameters = []
        for name, param in lmfit_result.params.items():
            if param.min == float("-inf"):
                param.min = None
            if param.max == float("inf"):
                param.max = None
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

    def _reorder_free_symbols(self) -> List[str]:
        ordered_symbols = []
        symbols = self._symbols_list
        for symbol in symbols:
            if symbol not in [param.name for param in self.parameters]:
                ordered_symbols.append(symbol)

        if len(ordered_symbols) != 1:
            raise ValueError(
                "The signal equation must contain only one free symbol"
                f" {ordered_symbols} found."
            )
        for param in self.parameters:
            ordered_symbols.append(param.name)

        return ordered_symbols

    @property
    def _symbols_list(self):
        sympy_eq = sp.sympify(self.signal_equation)
        return [str(s) for s in list(sympy_eq.free_symbols)]

    @property
    def signal_callable(self) -> Tuple[callable, List[str]]:
        equation = sp.sympify(self.signal_equation)
        variables = self._reorder_free_symbols()
        callable = sp.lambdify(variables, equation)

        return callable, variables

    @property
    def init_param_dict(self) -> dict:
        return {p.name: p.init_value for p in self.parameters}

    @property
    def species_id(self) -> str:
        return self._reorder_free_symbols()[0]

    @property
    def param_dict(self):
        return {p.name: p.value for p in self.parameters}
