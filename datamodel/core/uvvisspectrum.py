import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List


class UVVisSpectrum(sdRDM.DataModel):

    concentration_unit: str = Field(
        ...,
        description="Concentration unit.",
    )

    concentration: List[float] = Field(
        description="Concentration at which spectrum is recorded.",
        default_factory=ListPlus,
    )

    wavelength: List[float] = Field(
        description="Wavelengths used for detection.",
        default_factory=ListPlus,
    )

    absorption: List[float] = Field(
        description="Measured absorption, corresponding to detection wavelengths.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/calibration_data.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="f6208fad433fc2ea4f2c2f4c333d1195160ac62e"
    )
