import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase

from .model import Model
from .standard import Standard
from .parameter import Parameter


@forge_signature
class Calibrator(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibratorINDEX"),
        xml="@id",
    )

    standard: Optional[Standard] = Field(
        default=Standard(),
        description="Standard data of a chemical species",
    )

    concentrations: List[float] = Field(
        description="Concentrations of the species",
        default_factory=ListPlus,
        multiple=True,
    )

    conc_unit: Optional[UnitBase] = Field(
        default=None,
        description="Concentration unit",
    )

    signals: List[float] = Field(
        description="Measured signals, corresponding to the concentrations",
        default_factory=ListPlus,
        multiple=True,
    )

    models: List[Model] = Field(
        description="Potential models, describing the standard data",
        default_factory=ListPlus,
        multiple=True,
    )

    cutoff: Optional[float] = Field(
        default=None,
        description=(
            "Upper cutoff value for the measured signal. All signals above this value"
            " will be ignored during calibration"
        ),
    )

    def add_to_models(
        self,
        name: Optional[str] = None,
        equation: Optional[str] = None,
        parameters: List[Parameter] = ListPlus(),
        aic: Optional[float] = None,
        bic: Optional[float] = None,
        r2: Optional[float] = None,
        residuals: List[float] = ListPlus(),
        rmsd: Optional[float] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Model' to attribute models

        Args:
            id (str): Unique identifier of the 'Model' object. Defaults to 'None'.
            name (): Name of the calibration model. Defaults to None
            equation (): Equation of the calibration model. Defaults to None
            parameters (): Parameters of the calibration model equation. Defaults to ListPlus()
            aic (): Akaike information criterion. Defaults to None
            bic (): Bayesian information criterion. Defaults to None
            r2 (): Coefficient of determination. Defaults to None
            residuals (): Residuals of the calibration model. Defaults to ListPlus()
            rmsd (): Root mean square deviation. Defaults to None
        """

        params = {
            "name": name,
            "equation": equation,
            "parameters": parameters,
            "aic": aic,
            "bic": bic,
            "r2": r2,
            "residuals": residuals,
            "rmsd": rmsd,
        }

        if id is not None:
            params["id"] = id

        self.models.append(Model(**params))

        return self.models[-1]
