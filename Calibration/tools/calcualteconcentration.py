from typing import Callable, Dict, List

from Calibration.tools.standardcurve import StandardCurve

from pyenzyme import EnzymeMLDocument

from scipy.optimize import fsolve
import numpy as np

# Applies 'StandardCurve' on an 'EnzymeMLDocument'.
def apply_StandardCurve_to_EnzymeML(
    enzmldoc: EnzymeMLDocument,
    standard_curve: StandardCurve,
    reactant_id: str,
    wavelength: int = None,
    model_name: str = None,
    ommit_nan_measurements: bool = False
    ) -> EnzymeMLDocument:

    max_absorption_standard_curve = max(standard_curve.absorption)

    delete_measurements = []

    for id, measurement in enzmldoc.measurement_dict.items():
        del_meas = False
        for rep, replicates in enumerate(measurement.getReactant(reactant_id).replicates):
            data = [x if x < max_absorption_standard_curve else float("nan") for x in replicates.data] # TODO add info if values are removed
            
            # Check if nan values are in measurement data
            if np.isnan(np.min(data)) and ommit_nan_measurements == True:
                del_meas = True
            else:
                conc = to_concentration(standard_curve, data, model_name)
                conc = [float(x) if x != 0 else float("nan") for x in conc] #retrieves nans from 'to_concentration', since fsolve outputs 0 if input is nan

                enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data = conc
                enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data_unit = standard_curve.concentration_unit
                enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data_type = "conc"
        if del_meas:
            delete_measurements.append(id)
    print(enzmldoc.measurement_dict.keys())
    for id in delete_measurements:
        del enzmldoc.measurement_dict[id]
    
    if len(delete_measurements) != 0:
        print(f"Measurements '{delete_measurements}' removed from document, since measurement values are out of calibration range, respectively.")

    return enzmldoc

def to_concentration(standard_curve: StandardCurve, array: list, model_name: str = None) -> List[float]:
    # TODO Extrapolation warning
    
    if not isinstance(array, np.ndarray):
        array = np.array(array)

    if model_name == None:
        model = standard_curve.models[next(iter(standard_curve.result_dict))]
    else:
        model = standard_curve.models[model_name]

    equation: Callable = equation_dict[model.name]

    concentration = []
    for absorption in array:
        params = model.parameters
        params["absorption"] = absorption
        concentration.append(float(fsolve(equation, 0, params)))

    return concentration



def root_linear1(x: float, params: Dict[str, float]) -> float:
    a, absorption = params.values()
    return a*x - absorption


def root_quadratic(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return a*x**2 + b*x - absorption


def root_poly3(x: float, params: Dict[str, float]) -> float:
    a, b, c, absorption = params.values()
    return a*x**3 + b*x**2 + c*x - absorption


def root_poly_e(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return a*np.exp(x/b) - absorption


def root_rational(x: float, params: Dict[str, float]) -> float:
    a, b, absorption = params.values()
    return (a*x)/(b+x) - absorption

# Mapper for equations from CalibrationModel
equation_dict: Dict[str, Callable] = {
    "Linear": root_linear1,
    "Quadratic": root_quadratic,
    "3rd polynominal": root_poly3,
    "Exponential": root_poly_e,
    "Rational": root_rational
    }


if __name__ == "__main__":
    from Calibration.core.standard import Standard
    from Calibration.core.calibration import Calibration

    import pyenzyme as pe
    
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
    

    enzmldoc = pe.EnzymeMLDocument.fromFile("/Users/maxhaussler/Dropbox/master_thesis/data/sdRDM_ABTS_oxidation/test_ABTS.omex")

    enzmldoc = apply_standard_curve(enzmldoc, standardcurce, "s0", ommit_nan_measurements=True)
    #print(enzmldoc.measurement_dict["m9"].species_dict["reactants"]["s0"].replicates[2].data)