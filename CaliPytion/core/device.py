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
        description="Device manufacturer",
    )

    model: Optional[str] = Field(
        default=None,
        description="Model name of the device",
    )

    software_version: Optional[str] = Field(
        default=None,
        description="Software version of the device",
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="ac2969a829fcebd4fea6bd449c02c1d4fefba4be"
    )
