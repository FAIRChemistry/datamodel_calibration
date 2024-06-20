from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class CalibrationRange(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """Defines the concentration and signal bounds in which the calibration model is valid."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    conc_lower: Optional[float] = element(
        description="Lower concentration bound of the model",
        default=None,
        tag="conc_lower",
        json_schema_extra=dict(),
    )

    conc_upper: Optional[float] = element(
        description="Upper concentration bound of the model",
        default=None,
        tag="conc_upper",
        json_schema_extra=dict(),
    )

    signal_lower: Optional[float] = element(
        description="Lower signal bound of the model",
        default=None,
        tag="signal_lower",
        json_schema_extra=dict(),
    )

    signal_upper: Optional[float] = element(
        description="Upper signal bound of the model",
        default=None,
        tag="signal_upper",
        json_schema_extra=dict(),
    )

    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="a585b33c1c23f94d0f82ae18fd86ca3a2eb9188b"
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
