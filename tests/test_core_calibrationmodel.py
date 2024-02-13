from CaliPytion.core.calibrationmodel import CalibrationModel 

def test_replace_conc_with_species_id():
    model = CalibrationModel(
        name="test_model",
        signal_equation="conc * a"
    )

    model._replace_equction_id("species_id")
    assert model.signal_equation == "species_id * a"

def test_replace_concentration_with_species_id():
    model = CalibrationModel(
        name = "test_model",
        signal_equation = "a * concentration + concentration**b"
    )
    model._replace_equction_id("s0")
    print(model.signal_equation)
    assert model.signal_equation == "a * s0 + s0**b"

def test_no_replace():
    model = CalibrationModel(
        name="test_model",
        signal_equation="a * s0 + s0**b"
    )
    model._replace_equction_id("s0")
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