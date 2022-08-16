import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import Optional


class Device(sdRDM.DataModel):

    device_manufacturer: Optional[str] = Field(
        description="Device manufacturer.",
        default=None,
    )

    device_model: Optional[str] = Field(
        description="Model name of the device.",
        default=None,
    )

    device_software_version: Optional[str] = Field(
        description="Software version of the device.",
        default=None,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/calibration_data.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="7a9001e86a09f3bccc674d9fa143f7d0afac527e"
    )
