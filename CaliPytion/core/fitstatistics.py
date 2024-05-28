from typing import Dict, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature
from sdRDM.tools.utils import elem2dict


@forge_signature
class FitStatistics(
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

    aic: Optional[float] = element(
        description="Akaike information criterion",
        default=None,
        tag="aic",
        json_schema_extra=dict(),
    )

    bic: Optional[float] = element(
        description="Bayesian information criterion",
        default=None,
        tag="bic",
        json_schema_extra=dict(),
    )

    r2: Optional[float] = element(
        description="Coefficient of determination",
        default=None,
        tag="r2",
        json_schema_extra=dict(),
    )

    rmsd: Optional[float] = element(
        description="Root mean square deviation",
        default=None,
        tag="rmsd",
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
