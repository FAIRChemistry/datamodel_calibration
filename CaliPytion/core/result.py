import sdRDM

from typing import Optional, Union
from typing import List
from typing import Optional
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from .model import Model


@forge_signature
class Result(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("resultINDEX"),
        xml="@id",
    )

    concentration: List[float] = Field(
        description="Calculated concentration, based on the calibration model.",
        default_factory=ListPlus,
    )

    calibration_model: Optional[Model] = Field(
        description=(
            "Utilized calibration model and its parameters, leading to the calculated"
            " concentrations."
        ),
        default=None,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="58a83d25792cf5d447fc02017229a8241bf1d36a"
    )
