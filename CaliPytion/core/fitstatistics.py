import sdRDM

from typing import Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.utils import forge_signature, IDGenerator


@forge_signature
class FitStatistics(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("fitstatisticsINDEX"),
        xml="@id",
    )

    aic: Optional[float] = Field(
        default=None,
        description="Akaike information criterion",
    )

    bic: Optional[float] = Field(
        default=None,
        description="Bayesian information criterion",
    )

    r2: Optional[float] = Field(
        default=None,
        description="Coefficient of determination",
    )

    rmsd: Optional[float] = Field(
        default=None,
        description="Root mean square deviation",
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="071fa1dc4e3cdc585116bfd2049404e9b95560c4"
    )
