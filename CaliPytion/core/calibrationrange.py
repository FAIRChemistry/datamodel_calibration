import sdRDM

from typing import Optional
from pydantic import PrivateAttr
from uuid import uuid4
from pydantic_xml import attr, element
from sdRDM.base.utils import forge_signature


@forge_signature
class CalibrationRange(
    sdRDM.DataModel,
    nsmap={
        "": "https://github.com/FAIRChemistry/CaliPytion@0daea0e64ce2613de44d9c6c855c26093c755d38#CalibrationRange"
    },
):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    conc_lower: Optional[float] = element(
        description="Lower concentration bound of the model",
        default=None,
        tag="conc_lower",
        json_schema_extra=dict(),
    )

    conc_upper: Optional[float] = element(
        description="Upper concentration bound of the model",
        default=None,
        tag="conc_upper",
        json_schema_extra=dict(),
    )

    signal_lower: Optional[float] = element(
        description="Lower signal bound of the model",
        default=None,
        tag="signal_lower",
        json_schema_extra=dict(),
    )

    signal_upper: Optional[float] = element(
        description="Upper signal bound of the model",
        default=None,
        tag="signal_upper",
        json_schema_extra=dict(),
    )
    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="0daea0e64ce2613de44d9c6c855c26093c755d38"
    )
