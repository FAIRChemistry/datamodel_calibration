import sdRDM

from typing import Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.utils import forge_signature, IDGenerator


@forge_signature
class Device(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("deviceINDEX"),
        xml="@id",
    )

    manufacturer: Optional[str] = Field(
        default=None,
        description="Device manufacturer.",
    )

    model: Optional[str] = Field(
        default=None,
        description="Model name of the device.",
    )

    software_version: Optional[str] = Field(
        default=None,
        description="Software version of the device.",
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="94582cadc198cc7cd5ca0d4aae51f18e9e2d7289"
    )
