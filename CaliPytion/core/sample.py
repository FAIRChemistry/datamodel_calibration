import sdRDM

from typing import Optional
from pydantic import Field
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase


@forge_signature
class Sample(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("sampleINDEX"),
        xml="@id",
    )

    concentration: Optional[float] = Field(
        default=None,
        description="Concentration of the species",
    )

    conc_unit: Optional[UnitBase] = Field(
        default=None,
        description="Concentration unit",
    )

    signal: Optional[float] = Field(
        default=None,
        description="Measured signals at a given concentration of the species",
    )
