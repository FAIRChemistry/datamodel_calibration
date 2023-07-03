import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from datetime import date as Date
from pydantic import PositiveFloat

from .series import Series
from .device import Device
from .standard import Standard
from .spectrum import Spectrum
from .concentrationunits import ConcentrationUnits
from .temperatureunits import TemperatureUnits
from .result import Result


@forge_signature
class Calibration(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibrationINDEX"),
        xml="@id",
    )

    reactant_id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the calibrated reactant.",
    )

    date_measured: Optional[Date] = Field(
        default=None,
        description="Date when the calibration data was measured",
    )

    pH: Optional[PositiveFloat] = Field(
        default=None,
        description="pH of solution.",
    )

    temperature: Optional[PositiveFloat] = Field(
        default=None,
        description="Temperature during calibration.",
    )

    temperature_unit: Optional[TemperatureUnits] = Field(
        default=None,
        description="Temperature unit.",
    )

    device: Optional[Device] = Field(
        default=None,
        description="Device object, containing information about the analytic device.",
    )

    standard: List[Standard] = Field(
        description="Standard data of a substance.",
        default_factory=ListPlus,
        multiple=True,
    )

    spectrum: Optional[Spectrum] = Field(
        default=None,
        description="Spectrum data of a substance.",
    )

    result: Optional[Result] = Field(
        default=None,
        description=(
            "Contains calculated concentrations and information on the fitted"
            " calibration equation to calculate the concentrations."
        ),
    )

    def add_to_standard(
        self,
        wavelength: Optional[float] = None,
        concentration: List[float] = ListPlus(),
        concentration_unit: Optional[ConcentrationUnits] = None,
        absorption: List[Series] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Standard' to attribute standard

        Args:
            id (str): Unique identifier of the 'Standard' object. Defaults to 'None'.
            wavelength (): Detection wavelength.. Defaults to None
            concentration (): Concentration of the reactant.. Defaults to ListPlus()
            concentration_unit (): Concentration unit.. Defaults to None
            absorption (): Measured absorption, corresponding to the applied concentration of the reactant.. Defaults to ListPlus()
        """

        params = {
            "wavelength": wavelength,
            "concentration": concentration,
            "concentration_unit": concentration_unit,
            "absorption": absorption,
        }

        if id is not None:
            params["id"] = id

        self.standard.append(Standard(**params))

        return self.standard[-1]
