from typing import Dict, List, Optional
from uuid import uuid4

import sdRDM
from lxml.etree import _Element
from pydantic import PrivateAttr, model_validator
from pydantic_xml import attr, element
from sdRDM.base.listplus import ListPlus
from sdRDM.tools.utils import elem2dict

from .calibrationrange import CalibrationRange
from .fitstatistics import FitStatistics
from .parameter import Parameter


class CalibrationModel(
    sdRDM.DataModel,
    search_mode="unordered",
):
    """The CalibrationModel describes the calibration model which was fitted to the calibration data. The calibration model consists of the signal law and harbors the parameters of the calibration equation. The calibration range defines the concentration and signal bounds in which the calibration model is valid."""

    id: Optional[str] = attr(
        name="id",
        alias="@id",
        description="Unique identifier of the given object.",
        default_factory=lambda: str(uuid4()),
    )

    name: str = element(
        description="Name of the calibration model",
        tag="name",
        json_schema_extra=dict(),
    )

    molecule_id: Optional[str] = element(
        description="ID of the molecule like ChEBI ID.",
        default=None,
        tag="molecule_id",
        json_schema_extra=dict(),
    )

    signal_law: Optional[str] = element(
        description=(
            "Law describing the signal intensity as a function of the concentration"
        ),
        default=None,
        tag="signal_law",
        json_schema_extra=dict(),
    )

    parameters: List[Parameter] = element(
        description="Parameters of the calibration equation",
        default_factory=ListPlus,
        tag="parameters",
        json_schema_extra=dict(
            multiple=True,
        ),
    )

    molecule_symbol: Optional[str] = element(
        description="Symbol representing the molecule in the signal law",
        default=None,
        tag="molecule_symbol",
        json_schema_extra=dict(),
    )

    was_fitted: Optional[bool] = element(
        description="Indicates if the model was fitted to the data",
        default=False,
        tag="was_fitted",
        json_schema_extra=dict(),
    )

    calibration_range: Optional[CalibrationRange] = element(
        description=(
            "Concentration and signal bounds in which the calibration model is valid."
        ),
        default_factory=CalibrationRange,
        tag="calibration_range",
        json_schema_extra=dict(),
    )

    statistics: Optional[FitStatistics] = element(
        description="Fit statistics of the calibration model",
        default_factory=FitStatistics,
        tag="statistics",
        json_schema_extra=dict(),
    )

    _repo: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    _commit: Optional[str] = PrivateAttr(
        default="980959e98487dee71a92138065112ffc402baf1c"
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

    def add_to_parameters(
        self,
        symbol: Optional[str] = None,
        value: Optional[float] = None,
        init_value: Optional[float] = None,
        stderr: Optional[float] = None,
        lower_bound: Optional[float] = None,
        upper_bound: Optional[float] = None,
        id: Optional[str] = None,
        **kwargs,
    ) -> Parameter:
        """
        This method adds an object of type 'Parameter' to attribute parameters

        Args:
            id (str): Unique identifier of the 'Parameter' object. Defaults to 'None'.
            symbol (): Name of the parameter. Defaults to None
            value (): Value of the parameter. Defaults to None
            init_value (): Initial value of the parameter. Defaults to None
            stderr (): 1-sigma standard error of the parameter. Defaults to None
            lower_bound (): Lower bound of the parameter prior to fitting. Defaults to None
            upper_bound (): Upper bound of the parameter prior to fitting. Defaults to None
        """

        params = {
            "symbol": symbol,
            "value": value,
            "init_value": init_value,
            "stderr": stderr,
            "lower_bound": lower_bound,
            "upper_bound": upper_bound,
        }

        if id is not None:
            params["id"] = id

        obj = Parameter(**params)

        self.parameters.append(obj)

        return self.parameters[-1]
