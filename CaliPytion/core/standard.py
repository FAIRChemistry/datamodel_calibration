import sdRDM

from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator


from .concentrationunits import ConcentrationUnits
from .series import Series


@forge_signature
class Standard(sdRDM.DataModel):

    """Description of a standard curve."""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("standardINDEX"),
        xml="@id",
    )

    wavelength: Optional[float] = Field(
        default=None,
        description="Detection wavelength.",
    )

    concentration: List[float] = Field(
        default_factory=ListPlus,
        multiple=True,
        description="Concentration of the reactant.",
    )

    concentration_unit: Optional[ConcentrationUnits] = Field(
        default=None,
        description="Concentration unit.",
    )

    absorption: List[Series] = Field(
        default_factory=ListPlus,
        multiple=True,
        description=(
            "Measured absorption, corresponding to the applied concentration of the"
            " reactant."
        ),
    )

    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="94582cadc198cc7cd5ca0d4aae51f18e9e2d7289"
    )

    def add_to_absorption(
        self, values: List[float] = ListPlus(), id: Optional[str] = None
    ) -> None:
        """
        This method adds an object of type 'Series' to attribute absorption

        Args:
            id (str): Unique identifier of the 'Series' object. Defaults to 'None'.
            values (): Series representing an array of value. Defaults to ListPlus()
        """

        params = {
            "values": values,
        }

        if id is not None:
            params["id"] = id

        self.absorption.append(Series(**params))
