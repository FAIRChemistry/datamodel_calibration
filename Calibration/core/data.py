import sdRDM

from typing import Optional, Union
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from pydantic import Field
from typing import List
from typing import Optional

from .concentrationunits import ConcentrationUnits
from .series import Series
from .spectrum import Spectrum
from .standard import Standard


@forge_signature
class Data(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("dataINDEX"),
        xml="@id",
    )
    standard: List[Standard] = Field(
        description="Standard curve object, containing calibration data.",
        default_factory=ListPlus,
    )

    spectrum: Optional[Spectrum] = Field(
        description="UVVisSpectrum object, containing spectrum data.",
        default=None,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="07288e8a3ecc826d75ee928b58d2a9fb76fe14bc"
    )

    def add_to_standard(
        self,
        concentration: List[float],
        absorption: List[Series],
        wavelength: Optional[float] = None,
        concentration_unit: Optional[ConcentrationUnits] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        Adds an instance of 'Standard' to the attribute 'standard'.

        Args:
            id (str): Unique identifier of the 'Standard' object. Defaults to 'None'.
            concentration (List[float]): Concentration of the reactant.
            absorption (List[Series]): Measured absorption, corresponding to the applied concentration of the reactant.
            wavelength (Optional[float]): Detection wavelength. Defaults to None
            concentration_unit (Optional[ConcentrationUnits]): Concentration unit. Defaults to None
        """

        params = {
            "concentration": concentration,
            "absorption": absorption,
            "wavelength": wavelength,
            "concentration_unit": concentration_unit,
        }

        if id is not None:
            params["id"] = id

        standard = [Standard(**params)]

        self.standard = self.standard + standard
