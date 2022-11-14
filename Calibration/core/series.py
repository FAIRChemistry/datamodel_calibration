import sdRDM

from typing import Optional, Union
from typing import List
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


@forge_signature
class Series(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("seriesINDEX"),
        xml="@id",
    )

    values: List[float] = Field(
        description="Series representing an array of value", default_factory=ListPlus
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="bdadd49e3bc92f57bb84511721888175000cd011"
    )
