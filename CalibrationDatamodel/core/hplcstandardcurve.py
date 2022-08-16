from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List
from .standardcurve import StandardCurve


class HPLCStandardCurve(StandardCurve):

    peak_area: List[float] = Field(
        description="Measured peak area, corresponding to the applied concentration.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/calibration_data.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="00ee70107a0af02c17376203a67a0a655ed578b5"
    )
