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
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="c50b12ad7a7ac164d1be2c126d6e05557fb647f2"
    )
