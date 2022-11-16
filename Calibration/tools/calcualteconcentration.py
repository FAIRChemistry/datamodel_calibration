from typing import Callable, Dict, List

from Calibration.tools.standardcurve import StandardCurve

from pyenzyme import EnzymeMLDocument

from scipy.optimize import fsolve
import numpy as np


def calculate_concentration(
    enzmldoc: EnzymeMLDocument,
    standard_curve: StandardCurve,
    reactant_id: str,
    wavelength: int = None,
    model_name: str = None,
    ) -> EnzymeMLDocument:

    for id, measurement in enzmldoc.measurement_dict.items():
        for rep, replicates in enumerate(measurement.getReactant(reactant_id).replicates):
            conc = to_concentration(standard_curve, replicates.data, model_name)
            enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data = conc
            enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data_unit = standard_curve.concentration_unit
            enzmldoc.measurement_dict[id].species_dict["reactants"][reactant_id].replicates[rep].data_type = "conc"

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
    standardcurce = StandardCurve(calibration_data, 405)#.standard.absorption)
    

    enzmldoc = pe.EnzymeMLDocument.fromFile("/Users/maxhaussler/Dropbox/master_thesis/data/sdRDM_ABTS_oxidation/test_ABTS.omex")
    print(enzmldoc.measurement_dict["m3"].species_dict["reactants"]["s0"].replicates[2].data)

    enzmldoc = calculate_concentration(enzmldoc, standardcurce, "s0")
    print(enzmldoc.measurement_dict["m9"].species_dict["reactants"]["s0"].replicates[2].data)