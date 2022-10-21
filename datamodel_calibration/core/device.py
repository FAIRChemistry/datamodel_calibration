import sdRDM

from typing import Optional
from typing import Optional, Union
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


class Device(sdRDM.DataModel):
    device_manufacturer: Optional[str] = Field(
        description="Device manufacturer.", default=None
    )

    device_model: Optional[str] = Field(
        description="Model name of the device.", default=None
    )

    device_software_version: Optional[str] = Field(
        description="Software version of the device.", default=None
    )

    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("deviceINDEX"),
        xml="@id",
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="f6d13a0ec49b8e54167c7cf0705ac1ca2f68b325"
    )
