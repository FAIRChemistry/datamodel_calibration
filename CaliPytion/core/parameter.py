import sdRDM

from typing import Optional
from pydantic import Field, PrivateAttr
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
        description="Upper bound of the parameter",
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="3aaf24a354222900a29097170261308ff12ebff3"
    )
