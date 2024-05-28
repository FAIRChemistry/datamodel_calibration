from datetime import datetime as Datetime
from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict

from .calibrationmodel import CalibrationModel
from .sample import Sample
from .signaltype import SignalType


@forge_signature
class Standard(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Description of a standard measurement for an analyte"""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Name of the species",
        tag="name",
        json_schema_extra=dict(),
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

    samples: List[Sample] = element(
        description="Measured signal, at a given concentration of the species",
        default_factory=ListPlus,
        tag="samples",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    created: Optional[Datetime] = element(
        description="Date when the this file was created",
        default=None,
        tag="created",
        json_schema_extra=dict(),
    )

    modified: Optional[Datetime] = element(
        description="Date when the this file was last modified",
        default=None,
        tag="modified",
        json_schema_extra=dict(),
    )

    calibration_result: Optional[CalibrationModel] = element(
        description="The model which was used for concentration determination",
        default=None,
        tag="calibration_result",
        json_schema_extra=dict(),
    )

    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="adb1e995a49616fd3776b8b29a9a80b51ace21cd"
    )

    _raw_xml_data: Dict = PrivateAttr(default_factory=dict)

    @model_validator(mode="after")
    def _parse_raw_xml_data(self):
        for attr, value in self:
            if isinstance(value, (ListPlus, list)) and all(
                isinstance(i, _Element) for i in value
            ):
                self._raw_xml_data[attr] = [elem2dict(i) for i in value]
            elif isinstance(value, _Element):
                self._raw_xml_data[attr] = elem2dict(value)

        return self

    def add_to_samples(
        self,
        species_id: str,
        concentration: float,
        unit: str,
        signal: float,
        id: Optional[str] = None,
        **kwargs,
    ) -> Sample:
        """
        This method adds an object of type 'Sample' to attribute samples

        Args:
            id (str): Unique identifier of the 'Sample' object. Defaults to 'None'.
            species_id (): ID of the species.
            concentration (): Concentration of the species.
            unit (): Concentration unit.
            signal (): Measured signals at a given concentration of the species.
        """

        params = {
            "species_id": species_id,
            "concentration": concentration,
            "unit": unit,
            "signal": signal,
        }

        if id is not None:
            params["id"] = id

        obj = Sample(**params)

        self.samples.append(obj)

        return self.samples[-1]
