from datetime import datetime as Datetime
from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .calibrationmodel import CalibrationModel
from .sample import Sample
from .signaltype import SignalType


class Standard(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """The Standard describes the calibration data and the calibration model. The calibration data consists of the measured signal intensities at different concentrations of the molecule. The calibration model describes the relationship between the signal intensity and the concentration of the molecule. Furthermore, the valid concentration range defined by the underlying data is given."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    molecule_id: str = element(
        description="URI of the molecule (e.g. PubChem or ChEBI).",
        tag="molecule_id",
        json_schema_extra=dict(),
    )

    molecule_symbol: str = element(
        description="Symbol representing the molecule in the calibration equation.",
        tag="molecule_symbol",
        json_schema_extra=dict(),
    )

    ph: float = element(
        description="pH value of the solution.",
        tag="ph",
        json_schema_extra=dict(),
    )

    temperature: float = element(
        description="Temperature during calibration.",
        tag="temperature",
        json_schema_extra=dict(),
    )

    temp_unit: str = element(
        description="Temperature unit.",
        tag="temp_unit",
        json_schema_extra=dict(),
    )

    wavelength: Optional[float] = element(
        description="Detection wavelength in nm",
        default=None,
        tag="wavelength",
        json_schema_extra=dict(),
    )

    molecule_name: Optional[str] = element(
        description="Name of the molecule",
        default=None,
        tag="molecule_name",
        json_schema_extra=dict(),
    )

    signal_type: Optional[SignalType] = element(
        description="Quantity type of the signal intensity measured",
        default=None,
        tag="signal_type",
        json_schema_extra=dict(),
    )

    samples: List[Sample] = element(
        description="Measured signal, at a given concentration of the molecule",
        default_factory=ListPlus,
        tag="samples",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    created: Optional[Datetime] = element(
        description="Date when this file was created",
        default=None,
        tag="created",
        json_schema_extra=dict(),
    )

    result: Optional[CalibrationModel] = element(
        description="The model which was used for concentration determination",
        default=None,
        tag="result",
        json_schema_extra=dict(),
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
        concentration: float,
        conc_unit: str,
        signal: float,
        id: Optional[str] = None,
        **kwargs,
    ) -> Sample:
        """
        This method adds an object of type 'Sample' to attribute samples

        Args:
            id (str): Unique identifier of the 'Sample' object. Defaults to 'None'.
            concentration (): Concentration of the molecule..
            conc_unit (): Concentration unit.
            signal (): Measured signals at a given concentration of the molecule.
        """

        params = {
            "concentration": concentration,
            "conc_unit": conc_unit,
            "signal": signal,
        }

        if id is not None:
            params["id"] = id

        obj = Sample(**params)

        self.samples.append(obj)

        return self.samples[-1]
