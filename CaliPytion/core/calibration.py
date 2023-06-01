import sdRDM

from typing import Optional, Union
from typing import List
from typing import Optional
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from pydantic.types import PositiveFloat
from datetime import datetime
from .concentrationunits import ConcentrationUnits
from .device import Device
from .series import Series
from .spectrum import Spectrum
from .standard import Standard
from .temperatureunits import TemperatureUnits
from .result import Result


@forge_signature
class Calibration(sdRDM.DataModel):
    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibrationINDEX"),
        xml="@id",
    )

    reactant_id: Optional[str] = Field(
        description="Unique identifier of the calibrated reactant.", default=None
    )

    pH: Optional[PositiveFloat] = Field(description="pH of solution.", default=None)

    temperature: Optional[PositiveFloat] = Field(
        description="Temperature during calibration.", default=None
    )

    temperature_unit: Optional[TemperatureUnits] = Field(
        description="Temperature unit.", default=None
    )

    device: Optional[Device] = Field(
        description="Device object, containing information about the analytic device.",
        default=None,
    )

    standard: List[Standard] = Field(
        description="Standard data of a substance.", default_factory=ListPlus
    )

    spectrum: Optional[Spectrum] = Field(
        description="Spectrum data of a substance.", default=None
    )

    result: Optional[Result] = Field(
        description=(
            "Contains calculated concentrations and information on the fitted"
            " calibration equation to calculate the concentrations."
        ),
        default=None,
    )

    date: Optional[datetime] = Field(
        description="Date when the calibration data was measured", default=None
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="dba04b3c83b580af4ea49da8fcf2c0da47dca5a6"
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

    @classmethod
    def from_excel(
        cls,
        path: str,
        reactant_id: str,
        wavelength: float,
        concentration_unit: str,
        temperature: float = None,
        temperature_unit: str = None,
        pH: float = None,
        device_name: str = None,
        device_model: str = None,
        sheet_name: str = None,
    ):
        import pandas as pd

        df = pd.read_excel(path, sheet_name=sheet_name)
        concentration = df.iloc[:, 0].values
        absorptions = df.iloc[:, 1:]
        absorption_list = absorptions.values.T

        device = Device(manufacturer=device_name, model=device_model)

        absorption = []
        for abso in absorption_list:
            absorption.append(Series(values=list(abso)))

        standard = Standard(
            wavelength=wavelength,
            concentration=list(concentration),
            concentration_unit=concentration_unit,
            absorption=absorption,
        )

        return Calibration(
            reactant_id=reactant_id,
            pH=pH,
            temperature=temperature,
            temperature_unit=temperature_unit,
            device=device,
            standard=[standard],
        )
