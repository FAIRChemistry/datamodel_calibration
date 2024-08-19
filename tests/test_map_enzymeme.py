import math

import pyenzyme as pe
import pytest
from devtools import pprint
from pyenzyme.units import mM, nM, second

from calipytion import Calibrator
from calipytion.tools.enzymeml import convert_measurement
from calipytion.units import celsius as cal_celsius
from calipytion.units import mM as cal_mM

# create a mock calibrator
cal_data = {
    "molecule_id": "qweqwe123123",
    "molecule_name": "NADH",
    "ld_id": "www.example.com/qweqwe123123",
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
    "species_id": "qweqwe123123",
    "initial": 3,
    "prepared": 3,
    "data": [0.5, 1, 1.5, 2, 3.5],
    "data_unit": mM,
    "time": [0, 1, 2, 3, 4],
    "time_unit": second,
    "data_type": pe.DataTypes.ABSORBANCE,
}


def test_convert_measurement():
    ccal = Calibrator(**cal_data)
    print(ccal.models[0].signal_law)
    pprint(ccal)
    ccal.fit_models()
    ccal.create_standard(model=ccal.models[0], **standard_params)

    meas_data = pe.MeasurementData(**meas_data_dict)

    convert_measurement(ccal, ccal.standard.result, meas_data, extrapolate=False)
    print(meas_data.data)
    # assert rounded values
    assert [round(x, 1) for x in meas_data.data] == [5, 10, 15, 20, 35]
    assert meas_data.data_type == pe.DataTypes.CONCENTRATION


# test unit mismatch
def test_convert_measurement_unit_mismatch():
    ccal = Calibrator(**cal_data)
    ccal.fit_models()
    ccal.create_standard(model=ccal.models[0], **standard_params)

    meas_data = pe.MeasurementData(**meas_data_dict)
    meas_data.data_unit = nM

    # should raise a assertion error
    with pytest.raises(AssertionError):
        convert_measurement(ccal, ccal.standard.result, meas_data, extrapolate=False)


def test_convert_measurement_extrapolate_disabled_nan_produced():
    ccal = Calibrator(**cal_data)
    ccal.fit_models()
    ccal.create_standard(model=ccal.models[0], **standard_params)

    meas_data = pe.MeasurementData(**meas_data_dict)
    meas_data.data = [0.5, 1, 1.5, 2, 3.5, 5]

    convert_measurement(ccal, ccal.standard.result, meas_data, extrapolate=False)

    assert math.isnan(meas_data.data[-1])
    assert not math.isnan(meas_data.data[-2])
