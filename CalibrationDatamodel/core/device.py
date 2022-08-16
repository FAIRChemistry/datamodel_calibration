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
        default="00ee70107a0af02c17376203a67a0a655ed578b5"
    )
