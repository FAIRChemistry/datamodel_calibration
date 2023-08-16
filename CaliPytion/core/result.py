import sdRDM

from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from .model import Model


@forge_signature
class Result(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("resultINDEX"),
        xml="@id",
    )

    concentration: List[float] = Field(
        description="Calculated concentration, based on the calibration model",
        default_factory=ListPlus,
        multiple=True,
    )

    calibration_model: Optional[Model] = Field(
        default=Model(),
        description=(
            "Utilized calibration model and its parameters, leading to the calculated"
            " concentrations"
        ),
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="407f25c90534e881d0b6c83a47567723930bd3c3"
    )
