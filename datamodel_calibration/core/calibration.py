import sdRDM

import numpy as np
import pandas as pd
from typing import Optional
from typing import Optional, Union, Dict
from typing import Optional, Union
from typing import List
from pydantic import PrivateAttr
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from pydantic.types import PositiveFloat
from sdRDM.base.utils import forge_signature, IDGenerator

from .device import Device
from .data import Data


class Calibration(sdRDM.DataModel):
    reactant_id: Optional[str] = Field(
        description="Unique indentifier of the calibrated reactant.", default=None
    )

    device: Optional[Device] = Field(
        description="Device object, containing information about the analytic device.",
        default=None,
    )

    id: str = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibrationINDEX"),
        xml="@id",
    )

    date: Optional[str] = Field(
        description="Date when the calibration data was meeasured", default=None
    )

    pH: PositiveFloat = Field(..., description="pH of solution.")

    data: List[Data] = Field(
        description="Contains standard-curve and absorption-spectrum.",
        default_factory=ListPlus,
    )

    temperature: PositiveFloat = Field(
        ..., description="Temperature during calibration."
    )

    temperature_unit: TemperatureUnits = Field(..., description="Temperature unit.")

    __repo__: Optional[str] = PrivateAttr(
        default="git://github.com/FAIRChemistry/datamodel_calibration.git"
    )

    __commit__: Optional[str] = PrivateAttr(
        default="f6d13a0ec49b8e54167c7cf0705ac1ca2f68b325"
    )

    def SpectraMax190_StandardCurve(
        cls, path: str, species_wavelengths: Dict, replicates: int
    ):
        df = pd.read_excel(path, skiprows=17)
        temperature = df["Temperature(¡C)"].loc[0]

        df = df.drop(columns=["Unnamed: 0", "Temperature(¡C)"])
        df = df.dropna(how="all", axis=0)
        df = df.loc[:replicates]
        if isinstance(wavelengths, list) and len(wavelengths) > 1:
            n_concentrations = int(df.shape[1] / len(wavelengths))
            for wavelength in range(len(wavelengths)):
                if wavelength != 0:
                    df = df.drop(df.columns[n_concentrations * wavelength], axis=1)
            values = df.values.reshape(replicates, len(wavelengths), n_concentrations)
        else:
            n_concentrations = df.shape[1]
            values = df.values.reshape(replicates, n_concentrations)
        absorptions = []
        for replicate in values:
            absorptions.append(Series(values=list(replicate)))
        standard_curve = StandardCurve(temperature=temperature, temperature_unit="C")
        for replicate in values:
            standard_curve.add_to_absorption(list(replicate))
        instance = cls(
            device=Device(
                device_manufacturer="Molecular Devices",
                device_model="Spectra Max 190 Microplate Reader",
            ),
            standard_curve=standard_curve,
        )
        return instance
