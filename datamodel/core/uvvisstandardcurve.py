from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List
from .standardcurve import StandardCurve


class UVVisStandardCurve(StandardCurve):

    absorption: List[float] = Field(
        description="Measured absorption, corresponding to the applied concentration.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/calibration_data.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="f6208fad433fc2ea4f2c2f4c333d1195160ac62e"
    )
