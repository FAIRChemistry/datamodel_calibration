import sdRDM

from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase
from datetime import datetime as Datetime
from .signaltype import SignalType
from .sample import Sample
from .calibrationmodel import CalibrationModel


@forge_signature
class Standard(sdRDM.DataModel):
    """Description of a standard curve for an chemical species"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("standardINDEX"),
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

    wavelength: Optional[float] = Field(
        default=None,
        description="Detection wavelength in nm",
    )

    signal_type: Optional[SignalType] = Field(
        default=None,
        description="Quantity type of the signal intensity measured",
    )

    samples: List[Sample] = Field(
        description="Measured signal, at a given concentration of the species",
        default_factory=ListPlus,
        multiple=True,
    )

    ph: Optional[float] = Field(
        default=None,
        description="pH value of the solution",
    )

    temperature: Optional[float] = Field(
        default=None,
        description="Temperature during measurement",
    )

    temperature_unit: Optional[UnitBase] = Field(
        default=None,
        description="Temperature unit",
    )

    created: Optional[Datetime] = Field(
        default=None,
        description="Date when the standard curve was measured",
    )

    model_result: Optional[CalibrationModel] = Field(
        description="Model which was used for concentration determination",
        default_factory=CalibrationModel,
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="c3a3cdae1801d17461725162c77941fab16248d9"
    )

    def add_to_samples(
        self,
        concentration: Optional[float] = None,
        conc_unit: Optional[UnitBase] = None,
        signal: Optional[float] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Sample' to attribute samples

        Args:
            id (str): Unique identifier of the 'Sample' object. Defaults to 'None'.
            concentration (): Concentration of the species. Defaults to None
            conc_unit (): Concentration unit. Defaults to None
            signal (): Measured signals at a given concentration of the species. Defaults to None
        """
        params = {
            "concentration": concentration,
            "conc_unit": conc_unit,
            "signal": signal,
        }
        if id is not None:
            params["id"] = id
        self.samples.append(Sample(**params))
        return self.samples[-1]
