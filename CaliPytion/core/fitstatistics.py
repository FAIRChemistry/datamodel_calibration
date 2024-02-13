import sdRDM

from typing import Optional
from uuid import uuid4
from pydantic_xml import attr, element
from sdRDM.base.utils import forge_signature


@forge_signature
class FitStatistics(sdRDM.DataModel):
    """"""

    id: Optional[str] = attr(
        name="id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
        xml="@id",
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
