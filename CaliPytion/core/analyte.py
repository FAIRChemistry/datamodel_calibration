import sdRDM

from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from pydantic import PositiveFloat
from datetime import date as Date

from .concentrationunit import ConcentrationUnit
from .standard import Standard
from .series import Series
from .result import Result
from .device import Device
from .spectrum import Spectrum
from .temperatureunit import TemperatureUnit


@forge_signature
class Analyte(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("analyteINDEX"),
        xml="@id",
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the analyte",
    )

    inchi: Optional[str] = Field(
        default=None,
        description="InChi code of the analyte",
    )

    smiles: Optional[str] = Field(
        default=None,
        description="Smiles code of the analyte",
    )

    ph: Optional[PositiveFloat] = Field(
        default=None,
        description="pH of solution.",
    )

    temperature: Optional[PositiveFloat] = Field(
        default=None,
        description="Temperature during calibration",
    )

    temperature_unit: Optional[TemperatureUnit] = Field(
        default=None,
        description="Temperature unit.",
    )

    date_measured: Optional[Date] = Field(
        default=None,
        description="Date when the calibration data was measured",
    )

    device: Optional[Device] = Field(
        default=Device(),
        description="Device object, containing information about the analytic device",
    )

    standard: List[Standard] = Field(
        description="Standard data of a substance",
        default_factory=ListPlus,
        multiple=True,
    )

    spectrum: Optional[Spectrum] = Field(
        default=Spectrum(),
        description="Spectrum data of a substance",
    )

    result: Optional[Result] = Field(
        default=Result(),
        description=(
            "Contains calculated concentrations and information on the fitted"
            " calibration equation to calculate the concentrations."
        ),
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="407f25c90534e881d0b6c83a47567723930bd3c3"
    )

    def add_to_standard(
        self,
        wavelength: Optional[float] = None,
        concentration: List[float] = ListPlus(),
        concentration_unit: Optional[ConcentrationUnit] = None,
        absorption: List[Series] = ListPlus(),
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Standard' to attribute standard

        Args:
            id (str): Unique identifier of the 'Standard' object. Defaults to 'None'.
            wavelength (): Detection wavelength in nm. Defaults to None
            concentration (): Concentration of the reactant. Defaults to ListPlus()
            concentration_unit (): Concentration unit. Defaults to None
            absorption (): Measured absorption, corresponding to the applied concentration of the reactant. Defaults to ListPlus()
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
