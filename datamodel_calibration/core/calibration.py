import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from pydantic.types import PositiveFloat
from typing import Optional
from .device import Device
from .standardcurve import StandardCurve
from .uvvisspectrum import UVVisSpectrum


class Calibration(sdRDM.DataModel):

    calibration_id: Optional[str] = Field(
        description="Unique identifier for the calibration.",
        default=None,
    )

    reactant_id: Optional[str] = Field(
        description="Unique indentifier of the calibrated reactant.",
        default=None,
    )

    mixture_id: Optional[str] = Field(
        description="Unique indentifier of the calibrated mixture.",
        default=None,
    )

    solvent_name: Optional[str] = Field(
        description="Name of the used solvent.",
        default=None,
    )

    solvent_pH: Optional[float] = Field(
        inclusiveminimum=0,
        inclusivemaximum=14,
        description="pH of the solvent.",
        default=None,
    )

    solvent_concentration: Optional[PositiveFloat] = Field(
        description="Concentration of the solvent.",
        default=None,
    )

    solvent_concentration_unit: Optional[str] = Field(
        description="Solvent concentration unit.",
        default=None,
    )

    temperature: Optional[PositiveFloat] = Field(
        description="Temperature during calibration.",
        default=None,
    )

    temperature_unit: Optional[str] = Field(
        description="Temperature unit.",
        default=None,
    )

    device: Optional[Device] = Field(
        description="Device object, containing information about the analytic device.",
        default=None,
    )

    standard_curve: Optional[StandardCurve] = Field(
        description="Standard curve object, containing calibration data.",
        default=None,
    )

    uvvis_spectrum: Optional[UVVisSpectrum] = Field(
        description="UVVisSpectrum object, containing spectrum data",
        default=None,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="789d5828c81656f3d5269c5cfe1b8b83d5a8ed08"
    )
