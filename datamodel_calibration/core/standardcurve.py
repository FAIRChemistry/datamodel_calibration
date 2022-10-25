import sdRDM

from typing import Optional
from typing import List
from typing import Optional, Union
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from pydantic.types import PositiveFloat

from .series import Series


class StandardCurve(sdRDM.DataModel):
    wavelength: float = Field(..., description="Detection wavelength.")

    concentration_unit: str = Field(..., description="Concentration unit.")

    concentration: List[float] = Field(
        description="Concentration of the analyt.", default_factory=ListPlus
    )

    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("standardcurveINDEX"),
        xml="@id",
    )

    absorption: List[Series] = Field(
        description="Measured absorption, corresponding to the applied concentration.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="f6d13a0ec49b8e54167c7cf0705ac1ca2f68b325"
    )

    def add_to_absorption(self, values: List[float], id: Optional[str] = None) -> None:
        """
        Adds an instance of 'Series' to the attribute 'absorption'.

        Args:


            id (str): Unique identifier of the 'Series' object. Defaults to 'None'.


            values (List[float]): Series representing an array of value.
        """

        params = {"values": values}
        if id is not None:
            params["id"] = id
        absorption = [Series(**params)]
        self.absorption = self.absorption + absorption
