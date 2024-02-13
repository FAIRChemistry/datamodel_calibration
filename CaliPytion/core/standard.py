import sdRDM

from typing import List, Optional
from pydantic import PrivateAttr
from uuid import uuid4
from pydantic_xml import attr, element, wrapped
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from datetime import datetime as Datetime
from .calibrationmodel import CalibrationModel
from .signaltype import SignalType
from .sample import Sample


@forge_signature
class Standard(
    sdRDM.DataModel,
    nsmap={
        "": "https://github.com/FAIRChemistry/CaliPytion@26fef591b2c72fbebf9145b9ddec15843cb50c81#Standard"
    },
):
    """Description of a standard measurement for an analyte"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
    )

    species_id: Optional[str] = element(
        description="ID of the species",
        default=None,
        tag="species_id",
        json_schema_extra=dict(),
    )

    name: Optional[str] = element(
        description="Name of the species",
        default=None,
        tag="name",
        json_schema_extra=dict(),
    )

    wavelength: Optional[float] = element(
        description="Detection wavelength in nm",
        default=None,
        tag="wavelength",
        json_schema_extra=dict(),
    )

    signal_type: Optional[SignalType] = element(
        description="Quantity type of the signal intensity measured",
        default=None,
        tag="signal_type",
        json_schema_extra=dict(),
    )

    samples: List[Sample] = wrapped(
        "samples",
        element(
            description="Measured signal, at a given concentration of the species",
            default_factory=ListPlus,
            tag="Sample",
            json_schema_extra=dict(multiple=True),
        ),
    )

    ph: float = element(
        description="pH value of the solution",
        tag="ph",
        json_schema_extra=dict(),
    )

    temperature: float = element(
        description="Temperature during measurement",
        tag="temperature",
        json_schema_extra=dict(),
    )

    temperature_unit: str = element(
        description="Temperature unit",
        tag="temperature_unit",
        json_schema_extra=dict(),
    )

    created: Optional[Datetime] = element(
        description="Date when the standard curve was measured",
        default=None,
        tag="created",
        json_schema_extra=dict(),
    )

    calibration_result: Optional[CalibrationModel] = element(
        description="Model which was used for concentration determination",
        default=None,
        tag="calibration_result",
        json_schema_extra=dict(),
    )
    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="26fef591b2c72fbebf9145b9ddec15843cb50c81"
    )

    def add_to_samples(
        self,
        concentration: float,
        conc_unit: str,
        signal: float,
        id: Optional[str] = None,
    ) -> Sample:
        """
        This method adds an object of type 'Sample' to attribute samples

        Args:
            id (str): Unique identifier of the 'Sample' object. Defaults to 'None'.
            concentration (): Concentration of the species.
            conc_unit (): Concentration unit.
            signal (): Measured signals at a given concentration of the species.
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
