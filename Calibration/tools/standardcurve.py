from typing import Dict
from Calibration.core.calibration import Calibration
from Calibration.tools.calibrationmodel import CalibrationModel
from Calibration.tools.calibrationmodel import linear1, quadratic, poly3, poly_e, rational

from scipy.optimize import curve_fit
from lmfit.model import ModelResult
import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from pandas import DataFrame


class StandardCurve:
    def __init__(self, calibration_data: Calibration, wavelength: int = None):
        self.calibration_data = calibration_data
        self.wavelength = wavelength
        self.standard = self._get_Standard()
        self.concentration_unit = self.standard.concentration_unit
        self.substance_name = calibration_data.reactant_id
        self.wavelength = wavelength
        self._initialize_measurement_arrays()
        self.models = self._initialize_models()
        self._fit_models()

    def _initialize_measurement_arrays(self):
        absorption = [measurement.values for measurement in self.standard.absorption]
        n_replicates = len(absorption)

        self.concentration = np.tile(self.standard.concentration, n_replicates)
        self.absorption = np.array([measurement.values for measurement in self.standard.absorption]).flatten()

    def _get_Standard(self):
        if self.wavelength != None:
            try:
                print("try")
                return next(standard for standard in self.calibration_data.standard if standard.wavelength == self.wavelength)
            except:
                raise StopIteration(
                    f"No calibration data found for calibration at {self.wavelength} nm. Calibration data exists for following wavelengths: {[x.wavelength for x in self.calibration_data.standard]}")
        else:
            standard = self.calibration_data.standard[0]
            print(f"Found calibration data at {int(standard.wavelength)} nm")
            return standard


    def _initialize_models(self) -> Dict[str, CalibrationModel]:
        linear_model = CalibrationModel(
            name="Linear",
            equation=linear1,
            parameters={"a": 0.0}
        )
        quadratic_model = CalibrationModel(
            name="Quadratic",
            equation=quadratic,
            parameters={"a": 0.0, "b": 0.0}
        )
        poly3_model = CalibrationModel(
            name="3rd polynominal",
            equation=poly3,
            parameters={"a": 0.0, "b": 0.0, "c": 0.0}
        )
        polye_model = CalibrationModel(
            name="Exponential",
            equation=poly_e,
            parameters={"a": 0.0, "b": 0.0}
        )
        rational_model = CalibrationModel(
            name="Rational",
            equation=rational,
            parameters={"a": 0.0, "b": 0.0}
        )
        return {
            linear_model.name: linear_model,
            quadratic_model.name: quadratic_model,
            poly3_model.name: poly3_model,
            polye_model.name: polye_model,
            rational_model.name: rational_model}


    def _fit_models(self):
        for model in self.models.values():
            model.fit(self.absorption, self.concentration)

        self.result_dict = self._evaluate_aic()
        display(DataFrame.from_dict(self.result_dict, orient='index', columns=["AIC"]).rename(columns={0: "AIC"}).round().astype("int"))

    def _evaluate_aic(self):
        names = []
        aic = []
        for model in self.models.values():
            names.append(model.name)
            aic.append(model.result.aic)

        result_dict = dict(zip(names, aic))
        result_dict = dict(sorted(result_dict.items(), key=lambda item: item[1]))

        return result_dict


    def visualize(self, model_name: str = None):
        # TODO: add file directory for save
        if model_name is None:
            model = self.models[next(iter(self.result_dict.keys()))]
        else:
            model = self.models[model_name]

        smooth_x = np.linspace(
            self.concentration[0], self.concentration[-1], len(self.concentration)*2)

        equation = model.equation
        params = model.result.params.valuesdict()

        plt.scatter(self.concentration, self.absorption)
        plt.plot(smooth_x, equation(smooth_x, **params))
        plt.ylabel(f"absorption at {int(self.wavelength)} nm")
        plt.xlabel(f"{self.substance_name} [{self.concentration_unit}]")
        plt.title(f"calibration curve of {self.substance_name}")
        plt.show()


if __name__ == "__main__":
    from Calibration.core.standard import Standard

    standard = Standard(
        wavelength=405,
        concentration=[0.1, 0.5, 1, 2.5, 5, 10],
        concentration_unit="mM"
    )
    standard.add_to_absorption(
        values=[0.24, 0.46, 0.68, 1, 1.61, 2.39])
    standard.add_to_absorption(
        values=[0.2, 0.4, 0.6, 1, 1.6, 2.3])
    standard.add_to_absorption(
        values=[0.27, 0.43, 0.63, 1.9, 1.66, 2.31])



    calibration_data = Calibration(
        reactant_id="test chemical",
        pH=6.9,
        date="14.11.22",
        temperature=40,
        temperature_unit="C",
        standard=[standard]
        )


    # Fitter

    standardcurce = StandardCurve(calibration_data)#.standard.absorption)
    print(standardcurce.__dict__)
    #standardcurce.visualize()