import pytest
from CaliPytion.core.calibrationmodel import CalibrationModel 
import numpy as np
import numpy.testing as npt

def test_replace_conc_with_species_id():
    model = CalibrationModel(
        name="test_model",
        signal_equation="conc * a"
    )

    model._replace_equation_symbols("conc", "species_id")
    assert model.signal_equation == "species_id * a"

def test_replace_concentration_with_species_id():
    model = CalibrationModel(
        name = "test_model",
        signal_equation = "a * concentration + concentration**b"
    )
    model._replace_equation_symbols("concentration" ,"s0")
    print(model.signal_equation)
    assert model.signal_equation == "a * s0 + s0**b"

def test_no_replace():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * s0 + s0**b"
    )
    model._replace_equation_symbols("s0", "s0")
    assert model.signal_equation == "a * s0 + s0**b"

def test_returns_list_of_symbols():
    model = CalibrationModel(
        name="test_model",
        signal_equation = "a * x + b * x + c * x"
    )
    symbols_list = model._symbols_list
    assert isinstance(symbols_list, list)
    assert len(symbols_list) == 4
    assert "a" in symbols_list
    assert "x" in symbols_list
    assert "b" in symbols_list

def test_returns_list_of_signals_when_model_fitted():
    model = CalibrationModel(
        name="test_model",
        signal_equation = "a * x + b"
    )
    model.add_parameter(name="a", value=2.0)
    model.add_parameter(name="b", value=1.0)
    model.was_fitted = True

    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    expected_signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    assert model.calculate_signals(concentrations)[-2] == expected_signals[-2]
    assert model.calculate_signals(concentrations)[0] == expected_signals[0]

def test_handles_list_of_concentrations_length_1():
    model = CalibrationModel(
        name="test_model",
        signal_equation = "a * x + b"
    )
    model.add_parameter(name="a", value=2.0)
    model.add_parameter(name="b", value=1.0)
    model.was_fitted = True

    concentrations = [1.0]
    expected_signals = [3.0]
    assert model.calculate_signals(concentrations) == expected_signals

def test_raises_value_error_if_model_not_fitted():
    model = CalibrationModel(
        name="test_model",
        signal_equation = "a * x + b"
    )
    model.add_parameter(name="a", value=2.0)
    model.add_parameter(name="b", value=1.0)

    concentrations = [1.0, 2.0, 3.0]
    with pytest.raises(ValueError):
        model.calculate_signals(concentrations)

def test_returns_empty_list_if_given_empty_list_of_concentrations():
    model = CalibrationModel(
        name="test_model",
        signal_equation = "a * x + b"
    )
    model.add_parameter(name="a", value=2.0)
    model.add_parameter(name="b", value=1.0)
    model.was_fitted = True

    concentrations = []
    expected_signals = []
    assert model.calculate_signals(concentrations) == expected_signals

def test_calculate_concentrations_within_calibration_range():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
        
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    model.fit(concentrations, signals)
    assert model.calculate_concentrations(signals) == concentrations

def test_calculate_concentrations_with_nan_values():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
    
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, float("nan"), 7.0, float("nan"), 11.0]
    model.fit(concentrations, signals)
    npt.assert_allclose(
        actual=model.calculate_concentrations(signals),
        desired=[1.0, np.nan, 3.0, np.nan, 5.0],
        equal_nan=True
    )

def test_calculate_concentrations_model_not_fitted():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
    
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    with pytest.raises(ValueError):
        model.calculate_concentrations(signals)

def test_calculate_concentrations_all_nan_values():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
    
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    query_signals = [np.nan, np.nan, np.nan, np.nan, np.nan]
    model.fit(concentrations, signals)
    npt.assert_allclose(
        actual=model.calculate_concentrations(query_signals),
        desired=[np.nan, np.nan, np.nan, np.nan, np.nan],
        equal_nan=True
    )

def test_calculate_concentrations_replace_extrapolated_with_nan():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
    
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    query_signals = [0.0, 5.0, 7.0, 9.0, 11.0, 100]
    model.fit(concentrations, signals)
    npt.assert_allclose(
        actual=model.calculate_concentrations(query_signals),
        desired=[np.nan, 2.0, 3.0, 4.0, 5.0, np.nan],
        equal_nan=True
    )

def test_calculate_concentrations_extrapolat():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * x + b",
    
    )
    model._create_parameters("x")
    concentrations = [1.0, 2.0, 3.0, 4.0, 5.0]
    signals = [3.0, 5.0, 7.0, 9.0, 11.0]
    query_signals = [5.0, 13.0]
    model.fit(concentrations, signals)
    assert model.calculate_concentrations(query_signals, extrapolate=True) == [2.0, 6.0]
