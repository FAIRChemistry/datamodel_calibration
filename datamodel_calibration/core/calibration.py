import sdRDM

from typing import Optional
from typing import Optional, Union
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from pydantic.types import PositiveFloat
from sdRDM.base.utils import forge_signature, IDGenerator

from .device import Device
from .standardcurve import StandardCurve
from .spectrum import Spectrum


class Calibration(sdRDM.DataModel):
    reactant_id: Optional[str] = Field(
        description="Unique indentifier of the calibrated reactant.", default=None
    )

    device: Optional[Device] = Field(
        description="Device object, containing information about the analytic device.",
        default=None,
    )

    standard_curve: Optional[StandardCurve] = Field(
        description="Standard curve object, containing calibration data.", default=None
    )

    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibrationINDEX"),
        xml="@id",
    )

    spectrum: Optional[Spectrum] = Field(
        description="UVVisSpectrum object, containing spectrum data", default=None
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="f6d13a0ec49b8e54167c7cf0705ac1ca2f68b325"
    )
