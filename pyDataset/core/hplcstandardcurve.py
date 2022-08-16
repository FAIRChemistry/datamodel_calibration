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
        default="5c839fb92ce95dccfd2261983ba4f52778c7c662"
    )
