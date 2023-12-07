import sdRDM

import os
from typing import List, Optional
from pydantic import Field, PrivateAttr
from sdRDM import DataModel
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase
from datetime import datetime as Datetime
from pathlib import Path
from .calibrationmodel import CalibrationModel
from .sample import Sample
from .signaltype import SignalType
from ..ioutils import map_standard_to_animl


@forge_signature
class Standard(sdRDM.DataModel):
    """Description of a standard curve for an chemical species"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("standardINDEX"),
        xml="@id",
    )

    species_id: Optional[str] = Field(
        default=None,
        description="ID of the species",
    )

    name: Optional[str] = Field(
        default=None,
        description="Name of the species",
    )

    wavelength: Optional[float] = Field(
        default=None,
        description="Detection wavelength in nm",
    )

    signal_type: Optional[SignalType] = Field(
        default=None,
        description="Quantity type of the signal intensity measured",
    )

    samples: List[Sample] = Field(
        description="Measured signal, at a given concentration of the species",
        default_factory=ListPlus,
        multiple=True,
    )

    ph: Optional[float] = Field(
        default=None,
        description="pH value of the solution",
    )

    temperature: Optional[float] = Field(
        default=None,
        description="Temperature during measurement",
    )

    temperature_unit: Optional[UnitBase] = Field(
        default=None,
        description="Temperature unit",
    )

    created: Optional[Datetime] = Field(
        default=None,
        description="Date when the standard curve was measured",
    )

    model_result: Optional[CalibrationModel] = Field(
        description="Model which was used for concentration determination",
        default_factory=CalibrationModel,
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="3aaf24a354222900a29097170261308ff12ebff3"
    )

    def add_to_samples(
        self,
        concentration: Optional[float] = None,
        conc_unit: Optional[UnitBase] = None,
        signal: Optional[float] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Sample' to attribute samples

        Args:
            id (str): Unique identifier of the 'Sample' object. Defaults to 'None'.
            concentration (): Concentration of the species. Defaults to None
            conc_unit (): Concentration unit. Defaults to None
            signal (): Measured signals at a given concentration of the species. Defaults to None
        """
        params = {
            "concentration": concentration,
            "conc_unit": conc_unit,
            "signal": signal,
        }
        if id is not None:
            params["id"] = id
        self.samples.append(Sample(**params))
        return self.samples[-1]

    def to_animl(
        self, animl_document: "AnIML" = None, out_file: str | Path | os.PathLike = None
    ) -> None:
        """Map the Standard object to an AnIML document and serialize it
        as an XML document.

        Args:
            animl_document (AnIML, optional): Pass a pre-existing AnIML document to map Standard to. Defaults to None.
            out_file (str | Path | os.PathLike, optional): Desired path to AnIML output file. Defaults to None (current directory).
        """
        if not animl_document:
            try:
                animl_lib = DataModel.from_git(
                    url="https://github.com/FAIRChemistry/animl-specifications",
                    commit="0c51f12",
                )
                animl_document = animl_lib.AnIML()
            except Exception as e:
                print(
                    f"The following unexpected error has occured while "
                    + f"retrieving the AnIML data model from GitHub: "
                    + f"{type(e).__name__} - Is there a working "
                    + f"network connection?"
                )

        if not out_file:
            out_file = f"./standard_{str(Datetime.now().date())}.animl"

        map_standard_to_animl(standard=self, animl_document=animl_document)

        with open(out_file, "w") as f:
            f.write(animl_document.xml())

    @classmethod
    def from_animl(cls, path_to_animl_doc: str | Path | os.PathLike):
        """Parse a Standard object from one serialized to an AnIML
        document.

        Args:
            path_to_animl_doc (str | Path | os.PathLike): Path to an AnIML document.

        Returns:
            Standard: Standard object created from AnIML document.
        """
        raise NotImplementedError("Method `from_animl()` not yet implemented.")

        animl_document = DataModel.parse(path_to_animl_doc)

        ...

        return cls
