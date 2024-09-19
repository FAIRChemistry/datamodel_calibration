import json

import pyenzyme as pe
from pyenzyme.units import mM, second
from pytest import approx

from calipytion import Calibrator
from calipytion.units import celsius as cal_celsius
from calipytion.units import mM as cal_mM

# create a mock calibrator
cal_data = {
    "molecule_id": "s0",
    "molecule_name": "NADH",
    "pubchem_cid": 5893,
    "signals": [0, 1, 2, 3, 4],
    "concentrations": [0, 10, 20, 30, 40],
    "conc_unit": cal_mM,
}

standard_params = {
    "ph": 3,
    "temperature": 25,
    "temp_unit": cal_celsius,
}

meas_data_dict = {
    "species_id": "s0",
    "initial": 3,
    "prepared": 3,
    "data": [0.5, 1, 1.5, 2, 3.5],
    "data_unit": mM,
    "time": [0, 1, 2, 3, 4],
    "time_unit": second,
    "data_type": pe.DataTypes.ABSORBANCE,
}


def test_conversion_of_enzymeml_doc():
    # from devtools import pprint

    with open("tests/test_data/enzymeml.json") as f:
        data = json.load(f)

    doc = pe.EnzymeMLDocument(**data)

    ccal = Calibrator(**cal_data)
    ccal.fit_models()
    ccal.create_standard(model=ccal.models[0], **standard_params)

    ccal.apply_to_enzymeml(doc)
    assert doc.measurements[0].species_data[0].data_type == pe.DataTypes.CONCENTRATION
    assert doc.measurements[0].species_data[1].data_type == pe.DataTypes.CONCENTRATION
    assert approx(doc.measurements[0].species_data[0].data, abs=0.1) == [30, 20, 10, 0]
    assert approx(doc.measurements[1].species_data[0].data[1:], abs=0.1) == [
        30,
        20,
        10,
    ]


def test_conversion_of_enzymeml_doc_extrapolate():
    with open("tests/test_data/enzymeml.json") as f:
        data = json.load(f)

    doc = pe.EnzymeMLDocument(**data)

    ccal = Calibrator(**cal_data)
    ccal.fit_models()
    ccal.create_standard(model=ccal.models[0], **standard_params)

    ccal.apply_to_enzymeml(doc, extrapolate=True)

    assert doc.measurements[1].species_data[0].data[0] == approx(40, abs=0.1)
