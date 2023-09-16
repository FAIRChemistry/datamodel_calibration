import sdRDM

from typing import List, Optional
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase

from .parameter import Parameter
from .fitstatistics import FitStatistics
from .standard import Standard
from .calibrationrange import CalibrationRange
from .calibrationmodel import CalibrationModel


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

    models: List[CalibrationModel] = Field(
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
        was_fitted: Optional[bool] = None,
        calibration_range: Optional[CalibrationRange] = None,
        statistics: Optional[FitStatistics] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'CalibrationModel' to attribute models

        Args:
            id (str): Unique identifier of the 'CalibrationModel' object. Defaults to 'None'.
            name (): Name of the calibration model. Defaults to None
            equation (): Equation of the calibration model. Defaults to None
            parameters (): Parameters of the calibration model equation. Defaults to ListPlus()
            was_fitted (): Indicates if the model was fitted to the data. Defaults to None
            calibration_range (): Concentration and signal bounds in which the calibration model is valid.. Defaults to None
            statistics (): Fit statistics of the calibration model. Defaults to None
        """

        params = {
            "name": name,
            "equation": equation,
            "parameters": parameters,
            "was_fitted": was_fitted,
            "calibration_range": calibration_range,
            "statistics": statistics,
        }

        if id is not None:
            params["id"] = id

        self.models.append(CalibrationModel(**params))

        return self.models[-1]
