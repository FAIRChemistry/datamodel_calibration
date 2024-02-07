import sdRDM

from typing import Optional
from uuid import uuid4
from pydantic_xml import attr, element
from sdRDM.base.utils import forge_signature


@forge_signature
class Parameter(sdRDM.DataModel):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    name: Optional[str] = element(
        description="Name of the parameter",
        default=None,
        tag="name",
        json_schema_extra=dict(),
    )

    value: Optional[float] = element(
        description="Value of the parameter",
        default=None,
        tag="value",
        json_schema_extra=dict(),
    )

    init_value: Optional[float] = element(
        description="Initial value of the parameter",
        default=None,
        tag="init_value",
        json_schema_extra=dict(),
    )

    standard_error: Optional[float] = element(
        description="Standard error of the parameter",
        default=None,
        tag="standard_error",
        json_schema_extra=dict(),
    )

    lower_bound: Optional[float] = element(
        description="Lower bound of the parameter",
        default=None,
        tag="lower_bound",
        json_schema_extra=dict(),
    )

    upper_bound: Optional[float] = element(
        description="Upper bound of the parameter",
        default=None,
        tag="upper_bound",
        json_schema_extra=dict(),
    )
