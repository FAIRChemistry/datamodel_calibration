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
        default="a2fe424abb8bb04d454c1f1324ee3d85f77bfa77"
    )
