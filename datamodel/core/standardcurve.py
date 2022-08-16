import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List


class StandardCurve(sdRDM.DataModel):

    wavelength: float = Field(
        ...,
        description="Detection wavelength.",
    )

    concentration_unit: str = Field(
        ...,
        description="Concentration unit.",
    )

    concentration: List[float] = Field(
        description="Concentration of the analyt.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/calibration_data.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="7f890d3ea61d95a300cd17bbcef9ff3730c49a0e"
    )
