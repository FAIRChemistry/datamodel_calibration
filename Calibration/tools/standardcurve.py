from typing import Dict, List, Callable
from Calibration.core.calibration import Calibration
from Calibration.tools.calibrationmodel import CalibrationModel
from Calibration.tools.calibrationmodel import linear1, quadratic, poly3, poly_e, rational, root_linear1, root_poly3, root_poly_e, root_quadratic, root_rational, equation_dict

import matplotlib.pyplot as plt
import numpy as np
from IPython.display import display
from pandas import DataFrame
from pyenzyme import EnzymeMLDocument
from scipy.optimize import fsolve

# TODO calcualte method to abso --> conc

class StandardCurve:
    def __init__(self, calibration_data: Calibration, wavelength: int = None, blanc_data: bool = True, cutoff_absorption: float = None):
        self.blank_data = blanc_data
        self.cutoff = cutoff_absorption
        self.calibration_data = calibration_data
        self.wavelength = wavelength
        self.standard = self._get_Standard()
        self.concentration_unit = self.standard.concentration_unit
        self.substance_name = calibration_data.reactant_id
        self._initialize_measurement_arrays()
        self.models = self._initialize_models()
        self._fit_models()

    def _initialize_measurement_arrays(self):
        absorption = [measurement.values for measurement in self.standard.absorption]
        n_replicates = len(absorption)

        self.concentration = np.tile(self.standard.concentration, n_replicates)
        if self.blank_data and np.any(self.concentration == 0):
            pos = int(np.where(np.array(self.standard.concentration) == 0)[0])
            absorption = np.array([])
            for repeat in self.standard.absorption:
                absorption = np.append(absorption, [x - repeat.values[pos] for x in repeat.values])
            print("Calibration data was automatically blanked.")
            self.absorption = absorption
        else:
            self.absorption = np.array([measurement.values for measurement in self.standard.absorption]).flatten()
        
        if self.cutoff != None:
            self._cutoff_absorption()

    def _get_Standard(self):
        if self.wavelength != None:
            try:
                return next(standard for standard in self.calibration_data.standard if standard.wavelength == self.wavelength)
            except:
                raise StopIteration(
                    f"No calibration data found for calibration at {self.wavelength} nm. Calibration data exists for following wavelengths: {[x.wavelength for x in self.calibration_data.standard]}")
        else:
            standard = self.calibration_data.standard[0]
            print(f"Found calibration data at {int(standard.wavelength)} nm")
            self.wavelength = standard.wavelength
            return standard

    def _cutoff_absorption(self):
        pos = np.where(self.absorption < self.cutoff)
        self.concentration = self.concentration[pos]
        self.absorption = self.absorption[pos]


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

    def get_concentration(self, absorption: List[float], model_name: str = None) -> List[float]:
        
        # Convert to ndarray for performance
        if not isinstance(absorption, np.ndarray):
            absorption = np.array(absorption)

        # Select model equation
        if model_name == None:
            model = self.models[next(iter(self.result_dict))]
        else:
            model = self.models[model_name]
        equation: Callable = equation_dict[model.name]

        # Calculate concentration through roots
        concentration = []
        for value in absorption:
            params = model.parameters
            params["absorption"] = value
            concentration.append(float(fsolve(equation, 0, params)))

        return concentration

    def apply_to_EnzymeML(
        self,
        enzmldoc: EnzymeMLDocument,
        species_id: str,
        model_name: str = None,
        ommit_nan_measurements: bool = False
        ) -> EnzymeMLDocument:

        max_absorption_standard_curve = max(self.absorption)

        delete_measurements = []

        for id, measurement in enzmldoc.measurement_dict.items():
            del_meas = False
            for rep, replicates in enumerate(measurement.getReactant(species_id).replicates):
                data = [x if x < max_absorption_standard_curve else float("nan") for x in replicates.data] # TODO add info if values are removed
                
                # Check if nan values are in measurement data
                if np.isnan(np.min(data)) and ommit_nan_measurements == True:
                    del_meas = True
                else:
                    conc = self.get_concentration(absorption=data, model_name=model_name)
                    conc = [float(x) if x != 0 else float("nan") for x in conc] #retrieves nans from 'to_concentration', since fsolve outputs 0 if input is nan

                    enzmldoc.measurement_dict[id].species_dict["reactants"][species_id].replicates[rep].data = conc
                    enzmldoc.measurement_dict[id].species_dict["reactants"][species_id].replicates[rep].data_unit = self.concentration_unit
                    enzmldoc.measurement_dict[id].species_dict["reactants"][species_id].replicates[rep].data_type = "conc"
            if del_meas:
                delete_measurements.append(id)
        for id in delete_measurements:
            del enzmldoc.measurement_dict[id]
        
        if len(delete_measurements) != 0:
            print(f"Measurements '{delete_measurements}' removed from document, since respective measurement values are out of calibration range.")

        return enzmldoc



if __name__ == "__main__":
    from Calibration.core.standard import Standard

    standard = Standard(
        wavelength=405,
        concentration=[0.1, 0.5],
        concentration_unit="mole / l"
    )
    standard.add_to_absorption(
        values=[0.00004,0.00005])
    standard.add_to_absorption(
        values=[0.00004,0.00005])
    standard.add_to_absorption(
        values=[0.00004,0.00005])



    calibration_data = Calibration(
        reactant_id="test chemical",
        pH=6.9,
        date="14.11.22",
        temperature=40,
        temperature_unit="C",
        standard=[standard]
        )
    standardcurce = StandardCurve(calibration_data, 405)#.standard.absorption)

    #print(to_concentration(standardcurce, [0.1,0.33,float("nan"),1.3,0.6]))
    

    enzmldoc = EnzymeMLDocument.fromFile("/Users/maxhaussler/Dropbox/master_thesis/data/sdRDM_ABTS_oxidation/test_ABTS.omex")

    enzmldoc = standardcurce.apply_to_EnzymeML(enzmldoc, "s0", ommit_nan_measurements=True)
    #print(enzmldoc.measurement_dict["m9"].species_dict["reactants"]["s0"].replicates[2].data)