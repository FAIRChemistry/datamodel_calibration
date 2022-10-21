import sdRDM

from typing import Optional, Union
from typing import List
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from .series import Series


@forge_signature
class Spectrum(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("spectrumINDEX"),
        xml="@id",
    )

    concentration_unit: ConcentrationUnits = Field(
        ..., description="Concentration unit."
    )

    concentration: List[float] = Field(
        description="Concentration at which spectrum is recorded.",
        default_factory=ListPlus,
    )

    wavelength: List[float] = Field(
        description="Wavelengths used for detection.", default_factory=ListPlus
    )

    absorption: List[Series] = Field(
        description="Measured absorption, corresponding to detection wavelengths.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="fa7a9865e6c5d7599c7b37e3b3b00660f2071196"
    )

    def add_to_absorption(self, values: List[float], id: Optional[str] = None) -> None:
        """
        Adds an instance of 'Series' to the attribute 'absorption'.

        Args:


            id (str): Unique identifier of the 'Series' object. Defaults to 'None'.


            values (List[float]): Series representing an array of value.
        """

        params = {"values": values}
        if id is not None:
            params["id"] = id
        absorption = [Series(**params)]
        self.absorption = self.absorption + absorption
