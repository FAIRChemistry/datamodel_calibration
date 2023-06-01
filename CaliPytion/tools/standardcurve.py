from typing import Dict, List
from CaliPytion.core.calibration import Calibration
from CaliPytion.tools.calibrationmodel import CalibrationModel
from CaliPytion.core.device import Device
from CaliPytion.core.standard import Standard
from CaliPytion.core.series import Series
from CaliPytion.core.result import Result
from CaliPytion.core.model import Model
from CaliPytion.core.parameter import Parameter


from CaliPytion.tools.equations import linear, quadratic, poly_3, poly_e, rational

import matplotlib.pyplot as plt
import copy
from numpy import ndarray, mean, std, where, any, array, tile, linspace, isnan
import pandas as pd
from IPython.display import display
from pyenzyme import EnzymeMLDocument


class StandardCurve:
    def __init__(
        self,
        concentrations: list,
        signals: list,
        conc_unit: str = None,
        wavelength: int = None,
        analyte_name: str = None,
        blank_data: bool = True,
        cutoff_signal: float = None,
    ):
        self.concentrations = concentrations
        self.signals = signals
        self.conc_unit = conc_unit
        self.analyte_name = analyte_name
        self.blank_data = blank_data
        self.cutoff_signal = cutoff_signal
        self.wavelength = wavelength

        if blank_data:
            self.signals = self._blank_measurement_signal()
            print("Standard curve data was blanked.")

        if cutoff_signal:
            self._cutoff_signal()

        self.models = self._initialize_models()
        self._fit_models(concentrations=concentrations, signals=signals)

    def _blank_measurement_signal(self) -> List[float]:
        if any(self.concentrations == 0):
            pos = where(self.concentrations == 0)[0]
            mean_blank = mean(self.signals[pos])
            std_blank = std(self.signals[pos])
            percentual_std = std_blank / mean_blank

            if percentual_std > 0.05:
                print(
                    f"Standard deviation among blank measurements exceeds 5% ({percentual_std*100:.1f}%)"
                )

            return self.signals - mean_blank

        else:
            raise ValueError(
                f"No measurements with an analyte concentration of 0 {self.conc_unit} defined.\n\
                Set 'blank_data = False'."
            )

    def _cutoff_signal(self):
        pos = where(self.signals < self.cutoff_signal)
        self.concentrations = self.concentrations[pos]
        self.signals = self.signals[pos]

    def _initialize_models(self) -> Dict[str, CalibrationModel]:
        linear_model = CalibrationModel(
            name="Linear",
            equation=linear,
        )
        quadratic_model = CalibrationModel(
            name="Quadratic",
            equation=quadratic,
        )
        poly3_model = CalibrationModel(
            name="3rd degree polynominal",
            equation=poly_3,
        )
        polye_model = CalibrationModel(
            name="Exponential",
            equation=poly_e,
        )
        rational_model = CalibrationModel(
            name="Rational",
            equation=rational,
        )
        return {
            linear_model.name: linear_model,
            quadratic_model.name: quadratic_model,
            poly3_model.name: poly3_model,
            polye_model.name: polye_model,
            rational_model.name: rational_model,
        }

    def _fit_models(self, concentrations: ndarray, signals: ndarray):
        for model in self.models.values():
            model._fit(signals=self.signals, concentrations=self.concentrations)

        self.result_dict = self._evaluate_aic()

        # display(DataFrame.from_dict(self.result_dict, orient='index', columns=["AIC"]).rename(columns={0: "AIC"}).round().astype("int").style.set_table_attributes('style="font-size: 12px"'))

    def _evaluate_aic(self):
        names = []
        aic = []
        for model in self.models.values():
            names.append(model.name)
            aic.append(model.aic)

        result_dict = dict(zip(names, aic))
        result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1]))

        return result_dict

    def visualize(
        self,
        model_name: str = None,
        ax: plt.Axes = None,
        title: str = None,
        y_label: str = None,
    ):
        if ax is None:
            ax_provided = False
            ax = plt.gca()
        else:
            ax_provided = True

        if model_name is None:
            model = self.models[next(iter(self.result_dict.keys()))]
        else:
            model = self.models[model_name]

        smooth_x = linspace(
            self.concentrations[0],
            self.concentrations[-1],
            len(self.concentrations) * 2,
        )

        # equation = model.equation.lhs
        function, _ = model._get_np_function(
            model.equation, solve_for="signal", dependent_variable="concentration"
        )
        params = model.params

        ax.scatter(self.concentrations, self.signals)
        ax.plot(smooth_x, function(smooth_x, **params))
        if ax_provided == False:
            ax.set_ylabel(f"absorption at {int(self.wavelength)} nm")
            ax.set_xlabel(f"{self.analyte_name} [{self.conc_unit}]")
            ax.set_title(f"calibration curve of {self.analyte_name}")
        if title:
            ax.set_title(title)
        if y_label:
            print(f"{y_label}")
            ax.set_ylabel(y_label)

    def calculate_concentration(
        self,
        signals: List[float],
        model_name: str = None,
        allow_extrapolation: bool = False,
        values_only: bool = False,
    ) -> Result:
        # Check that input is provided as a list
        if not isinstance(signals, (list, ndarray)):
            raise ValueError("'signals' need to be provided as a list.")

        # Select calibration model (defaults to model with lowest AIC)
        if model_name == None:
            model = self.models[next(iter(self.result_dict))]
        else:
            model = self.models[model_name]
        # calculate concentrations
        concentrations = model.calculate_roots(
            signals=signals, allow_extrapolation=allow_extrapolation
        )

        if values_only:
            return concentrations

        else:
            parameters = [
                Parameter(name=key, value=value) for key, value in model.params.items()
            ]  # TODO: add stddev or uncertainty to Parameter class
            model = Model(
                name=model.name, equation=model.equation_string, parameters=parameters
            )
            print(f"result conc: {concentrations}")
            return Result(
                concentration=concentrations.tolist(), calibration_model=model
            )

    def apply_to_EnzymeML(
        self,
        enzmldoc: EnzymeMLDocument,
        species_id: str,
        model_name: str = None,
        ommit_nan_measurements: bool = False,
        allow_extrapolation: bool = False,
    ) -> EnzymeMLDocument:
        max_absorption_standard_curve = max(self.signals)

        delete_measurements = []

        enzmldoc = copy.deepcopy(enzmldoc)

        for id, measurement in enzmldoc.measurement_dict.items():
            del_meas = False
            for rep, replicates in enumerate(
                measurement.getReactant(species_id).replicates
            ):
                data = [
                    x if x < max_absorption_standard_curve else float("nan")
                    for x in replicates.data
                ]  # TODO add info if values are removed

                # Check if nan values are in measurement data
                if isnan(min(data)) and ommit_nan_measurements == True:
                    del_meas = True
                else:
                    result = self.calculate_concentration(
                        signals=data,
                        model_name=model_name,
                        allow_extrapolation=allow_extrapolation,
                    )

                    enzmldoc.measurement_dict[id].species_dict["reactants"][
                        species_id
                    ].replicates[rep].data = result.concentration
                    enzmldoc.measurement_dict[id].species_dict["reactants"][
                        species_id
                    ].replicates[rep].data_unit = self.conc_unit
                    enzmldoc.measurement_dict[id].species_dict["reactants"][
                        species_id
                    ].replicates[rep].data_type = "conc"
            if del_meas:
                delete_measurements.append(id)
        for id in delete_measurements:
            del enzmldoc.measurement_dict[id]

        if len(delete_measurements) != 0:
            print(
                f"Measurements '{delete_measurements}' removed from document, since respective measurement values are out of calibration range."
            )

        return enzmldoc

    @classmethod
    def from_datamodel(
        cls,
        calibration_data: Calibration,
        wavelength: float = None,
        blank_data: bool = True,
        cutoff_signal: float = None,
    ) -> "StandardCurve":
        # Get standard curve for given wavelength
        if wavelength != None:
            try:
                standard = next(
                    standard
                    for standard in calibration_data.standard
                    if standard.wavelength == wavelength
                )
            except:
                raise StopIteration(
                    f"No calibration data found for calibration at {wavelength} nm. Calibration data exists for following wavelengths: \
                        {[x.wavelength for x in calibration_data.standard]}"
                )
        else:
            standard = calibration_data.standard[0]
            wavelength = standard.wavelength
            print(f"Found calibration data at {float(standard.wavelength)} nm")

        # get concentrations and corresponding analyte signal
        concentrations = tile(standard.concentration, len(standard.absorption))
        signals = array(
            [measurement.values for measurement in standard.absorption]
        ).flatten()

        return cls(
            concentrations=concentrations,
            signals=signals,
            cutoff_signal=cutoff_signal,
            blank_data=blank_data,
            wavelength=wavelength,
            conc_unit=standard.concentration_unit,
            analyte_name=calibration_data.reactant_id,
        )  # TODO: add analyte name or id or inchi
