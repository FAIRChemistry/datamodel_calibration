import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator


@forge_signature
class Parameter(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("parameterINDEX"),
        xml="@id",
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the parameter",
    )

    value: Optional[float] = Field(
        default=None,
        description="Value of the parameter",
    )

    init_value: Optional[float] = Field(
        default=None,
        description="Initial value of the parameter",
    )

    standard_error: Optional[float] = Field(
        default=None,
        description="Standard error of the parameter",
    )

    lower_bound: Optional[float] = Field(
        default=None,
        description="Lower bound of the parameter",
    )

    upper_bound: Optional[float] = Field(
        default=None,
        description="Relative error of the parameter",
    )
