import sdRDM

from typing import Optional
from uuid import uuid4
from pydantic_xml import attr, element
from sdRDM.base.utils import forge_signature


@forge_signature
class Sample(sdRDM.DataModel):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    concentration: Optional[float] = element(
        description="Concentration of the species",
        default=None,
        tag="concentration",
        json_schema_extra=dict(),
    )

    conc_unit: Optional[str] = element(
        description="Concentration unit",
        default=None,
        tag="conc_unit",
        json_schema_extra=dict(),
    )

    signal: Optional[float] = element(
        description="Measured signals at a given concentration of the species",
        default=None,
        tag="signal",
        json_schema_extra=dict(),
    )
