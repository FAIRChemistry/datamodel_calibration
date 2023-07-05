import sdRDM

from typing import List, Optional
from pydantic import Field
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
        default=None,
        description=(
            "Utilized calibration model and its parameters, leading to the calculated"
            " concentrations"
        ),
    )
