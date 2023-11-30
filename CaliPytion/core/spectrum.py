import sdRDM

from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


@forge_signature
class Spectrum(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("spectrumINDEX"),
        xml="@id",
    )

    species_id: Optional[str] = Field(
        default=None,
        description="ID of the species",
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the species",
    )

    concentration: Optional[float] = Field(
        default=None,
        description="Concentration of the species",
    )

    conc_unit: List[float] = Field(
        description="Wavelengths of the spectrum",
        default_factory=ListPlus,
        multiple=True,
    )

    signals: List[float] = Field(
        default_factory=ListPlus,
        multiple=True,
        description="Measured signals, corresponding to detection wavelengths",
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="a596b28dd6e7d6dc47a30341f1f04cb4b78230a4"
    )
