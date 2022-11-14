import sdRDM

from typing import Optional, Union
from typing import List
from typing import Optional
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from .spectrum import Spectrum
from .standard import Standard


@forge_signature
class Data(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("dataINDEX"),
        xml="@id",
    )

    standard: List[Standard] = Field(
        description="Standard curve object, containing calibration data.",
        default_factory=ListPlus,
    )

    spectrum: Optional[Spectrum] = Field(
        description="UVVisSpectrum object, containing spectrum data.", default=None
    )

    test: Optional[str] = Field(description="test field.", default=None)

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="07288e8a3ecc826d75ee928b58d2a9fb76fe14bc"
    )
