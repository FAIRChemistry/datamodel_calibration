import sdRDM

from typing import Optional, Union
from typing import List
from typing import Optional
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from pydantic.types import PositiveFloat

from .concentrationunits import ConcentrationUnits
from .series import Series
from .spectrum import Spectrum
from .standardcurve import StandardCurve


@forge_signature
class Data(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("dataINDEX"),
        xml="@id",
    )

    standard_curve: List[StandardCurve] = Field(
        description="Standard curve object, containing calibration data.",
        default_factory=ListPlus,
    )

    spectrum: Spectrum = Field(
        description="UVVisSpectrum object, containing spectrum data", default=None
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="e1718b19020aa2c22565f1ef7eca350362ab53b8"
    )

    def add_to_standard_curve(
        self,
        wavelength: float,
        concentration: List[float],
        concentration_unit: ConcentrationUnits,
        absorption: List[Series],
        id: Optional[str] = None,
    ) -> None:
        """
        Adds an instance of 'StandardCurve' to the attribute 'standard_curve'.

        Args:


            id (str): Unique identifier of the 'StandardCurve' object. Defaults to 'None'.


            wavelength (float): Detection wavelength.


            concentration (List[float]): Concentration of the reactant.


            concentration_unit (ConcentrationUnits): Concentration unit.


            absorption (List[Series]): Measured absorption, corresponding to the applied concentration of the reactant.
        """

        params = {
            "wavelength": wavelength,
            "concentration": concentration,
            "concentration_unit": concentration_unit,
            "absorption": absorption,
        }
        if id is not None:
            params["id"] = id
        standard_curve = [StandardCurve(**params)]
        self.standard_curve = self.standard_curve + standard_curve
