import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List


class Series(sdRDM.DataModel):

    values: List[float] = Field(
        description="Series representing an array of values",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="f49b0dbafc2cf39fe26e15542bf10465e01cadca"
    )
