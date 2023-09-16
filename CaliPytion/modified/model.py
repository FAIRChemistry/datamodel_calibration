import copy
from typing import Dict
import sdRDM
import numpy as np


from lmfit import Model as LmfitModel
from lmfit.model import ModelResult

from typing import Callable, List, Optional, Tuple
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
import sympy as sp

from CaliPytion.core import standard


from .parameter import Parameter


@forge_signature
class Model(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("modelINDEX"),
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

    aic: Optional[float] = Field(
        default=None,
        description="Akaike information criterion",
    )

    bic: Optional[float] = Field(
        default=None,
        description="Bayesian information criterion",
    )

    r2: Optional[float] = Field(
        default=None,
        description="Coefficient of determination",
    )

    residuals: List[float] = Field(
        description="Residuals of the calibration model",
        default_factory=ListPlus,
        multiple=True,
    )

    rmsd: Optional[float] = Field(
        default=None,
        description="Root mean square deviation",
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
            standard_error (): Standard error of the parameter. Defaults to None
            lower_bound (): Lower bound of the parameter. Defaults to None
            upper_bound (): Relative error of the parameter. Defaults to None
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

        lmfit_result = lmfit_model.fit(data=signals, **parameters)

        # extract fit statistics
        self._extract_parameters(lmfit_result)
        self._extract_lmfit_statistics(lmfit_result)

        return lmfit_result

    def calculate_concentrations(
            self,
            signals: List[float],
            calibration_range: List[float],
            cutoff: float,
            allow_extrapolation: bool = False,
    ) -> List[float]:

        if not isinstance(signals, np.ndarray):
            signals = np.array(signals)

        # define calibration range of model
        min_conc = min(calibration_range)
        max_conc = max(calibration_range)

        # get root equation
        equality = self._get_equality()
        root_eq = equality.lhs - equality.rhs

        roots = []
        params = copy.copy(self._params)

        for signal in signals:
            if signal < cutoff:
                params[equality.rhs] = signal

                # calculate all possible real roots for equation
                roots.append(
                    list(sp.roots(sp.real_root(root_eq.subs(params))).keys())
                )
            else:
                roots.append([float("nan")])

        # reshape results, fill nan columns for signals above upper calibration range
        matrix = np.zeros(
            [len(roots), len(max(roots, key=lambda x: len(roots)))]) * np.nan

        # replace complex solutions with nans
        for i, j in enumerate(roots):
            without_complex = [float("nan") if isinstance(value, sp.core.add.Add)
                               else value for value in j]

            matrix[i][0: len(without_complex)] = without_complex

        roots = np.array(matrix).T

        # get root alternative with most values within calibration bonds
        n_values_in_calibration_range = []
        for result in roots:
            n_values_in_calibration_range.append(
                ((min_conc < result) & (result < max_conc)).sum()
            )

        correct_roots = roots[np.nanargmax(n_values_in_calibration_range)]

        if not allow_extrapolation:
            correct_roots[(min_conc > correct_roots) |
                          (max_conc < correct_roots)] = float("nan")

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
        )   # dependent variable needs to be in first pos for lmfit --> change of variable order

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
        self.aic = lmfit_result.aic
        self.bic = lmfit_result.bic
        self.r2 = lmfit_result.rsquared
        self.residuals = lmfit_result.residual.tolist()
        self.rmsd = self._calculate_rmsd(self.residuals)

    def _calculate_rmsd(self, residuals: np.ndarray) -> float:
        """Calculates root mean square deviation between measurements and fitted model."""
        residuals = np.array(residuals)
        return float(np.sqrt(sum(residuals**2) / len(residuals)))

    def _extract_parameters(
            self,
            lmfit_result: ModelResult,
    ):

        for name, param in lmfit_result.params.items():
            self.add_to_parameters(
                name=name,
                value=param.value,
                init_value=param.init_value,
                standard_error=param.stderr,
                lower_bound=param.min,
                upper_bound=param.max,
            )

    @property
    def _params(self) -> Dict[str, float]:
        return {param.name: param.value for param in self.parameters}
