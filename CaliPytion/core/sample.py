import sdRDM

from typing import Optional
from pydantic import PrivateAttr
from uuid import uuid4
from pydantic_xml import attr, element
from sdRDM.base.utils import forge_signature


@forge_signature
class Sample(
    sdRDM.DataModel,
    nsmap={
        "": "https://github.com/FAIRChemistry/CaliPytion@912965496c0bc570f5064b6e11b2f41a36d3366c#Sample"
    },
):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    concentration: float = element(
        description="Concentration of the species",
        tag="concentration",
        json_schema_extra=dict(),
    )

    conc_unit: str = element(
        description="Concentration unit",
        tag="conc_unit",
        json_schema_extra=dict(),
    )

    signal: float = element(
        description="Measured signals at a given concentration of the species",
        tag="signal",
        json_schema_extra=dict(),
    )
    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="912965496c0bc570f5064b6e11b2f41a36d3366c"
    )
