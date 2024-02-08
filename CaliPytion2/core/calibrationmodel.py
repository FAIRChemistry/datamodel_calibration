import sdRDM
import sympy as sp

from typing import List, Optional
from uuid import uuid4
from pydantic_xml import attr, element, wrapped
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from .parameter import Parameter
from .calibrationrange import CalibrationRange
from .fitstatistics import FitStatistics


@forge_signature
class CalibrationModel(sdRDM.DataModel):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    name: Optional[str] = element(
        description="Name of the calibration model",
        default=None,
        tag="name",
        json_schema_extra=dict(),
    )

    equation: Optional[str] = element(
        description="Equation for the measured signal",
        default=None,
        tag="equation",
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
        default=None,
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
    
    def _create_parameters(self, species_id: str):
        sympy_eq = sp.sympify(self.equation)
        symbols = [str(s) for s in list(sympy_eq.free_symbols)]


        if "conc" not in symbols and "concentration" not in symbols:
            raise ValueError("The equation must contain the variable 'conc' or 'concentration'")
        return sympy_eq
    
    def _replace_equction_id(self, species_id: str):
        if "conc" in self.equation:
            self.equation = self.equation.replace("conc", f"{species_id}")
        sympy_eq = self._create_parameters(species_id)
        for param in self.parameters:
            sympy_eq = sympy_eq.subs(sp.symbols(param.name), sp.symbols(f"{species_id}_{param.name}"))
        return sympy_eq

