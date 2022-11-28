import sdRDM

from typing import Optional, Union
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from pydantic import Field
from typing import Optional


@forge_signature
class Device(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("deviceINDEX"),
        xml="@id",
    )
    manufacturer: Optional[str] = Field(
        description="Device manufacturer.",
        default=None,
    )

    model: Optional[str] = Field(
        description="Model name of the device.",
        default=None,
    )

    software_version: Optional[str] = Field(
        description="Software version of the device.",
        default=None,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="1b5fbf69a0789d320ea9ab9f1e170acd5eb90aa6"
    )
