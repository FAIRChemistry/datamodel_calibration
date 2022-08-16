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
        default="a7e3ee023229f6fec5a1b53ded9339b3f404ab20"
    )
