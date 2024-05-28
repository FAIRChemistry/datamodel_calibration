from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict


class Parameter(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """"""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: Optional[str] = element(
        description="Name of the parameter",
        default=None,
        tag="name",
        json_schema_extra=dict(),
    )

    value: Optional[float] = element(
        description="Value of the parameter",
        default=None,
        tag="value",
        json_schema_extra=dict(),
    )

    init_value: Optional[float] = element(
        description="Initial value of the parameter",
        default=None,
        tag="init_value",
        json_schema_extra=dict(),
    )

    stderr: Optional[float] = element(
        description="1-sigma standard error of the parameter",
        default=None,
        tag="stderr",
        json_schema_extra=dict(),
    )

    lower_bound: Optional[float] = element(
        description="Lower bound of the parameter",
        default=None,
        tag="lower_bound",
        json_schema_extra=dict(),
    )

    upper_bound: Optional[float] = element(
        description="Upper bound of the parameter",
        default=None,
        tag="upper_bound",
        json_schema_extra=dict(),
    )

    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="6f0989db7cb73dc84b32fd3c4cdd72d759832e0a"
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
