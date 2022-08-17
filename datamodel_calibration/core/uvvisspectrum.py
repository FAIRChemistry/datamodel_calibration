import sdRDM


from typing import Optional
from pydantic import PrivateAttr
from sdRDM.base.listplus import ListPlus
from pydantic import Field
from typing import List
from .series import Series


class UVVisSpectrum(sdRDM.DataModel):

    concentration_unit: str = Field(
        ...,
        description="Concentration unit.",
    )

    concentration: List[float] = Field(
        description="Concentration at which spectrum is recorded.",
        default_factory=ListPlus,
    )

    wavelength: List[float] = Field(
        description="Wavelengths used for detection.",
        default_factory=ListPlus,
    )

    absorption: List[Series] = Field(
        description="Measured absorption, corresponding to detection wavelengths.",
        default_factory=ListPlus,
    )

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="f6d13a0ec49b8e54167c7cf0705ac1ca2f68b325"
    )

    def add_to_absorption(
        self,
        values: List[float] = ListPlus(),
    ) -> None:
        """
        Adds an instance of 'Series' to the attribute 'absorption'.

        Args:
            values (List[float]): Series representing an array of values.
        """

        self.absorption.append(
            Series(
                values=values,
            )
        )
