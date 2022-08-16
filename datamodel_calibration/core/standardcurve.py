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
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="bcf85adee583e97910f4e8e0a5d715ce6f99569f"
    )
