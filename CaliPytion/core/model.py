import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


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
            "standard_error": standard_error,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        }

        if id is not None:
            params["id"] = id

        self.parameters.append(Parameter(**params))

        return self.parameters[-1]
