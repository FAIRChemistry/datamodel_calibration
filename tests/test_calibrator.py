import json
from unittest.mock import MagicMock, patch

import pytest
from devtools import pprint

from calipytion import Calibrator
from calipytion.model import CalibrationModel, Parameter, Sample, Standard
from calipytion.units import C, mM

dummy_calibration = {
    "ld_id": "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17790",
    "molecule_id": "s1",
    "molecule_name": "Methanol",
    "concentrations": [0.2, 0.4, 0.6, 0.8, 1.0],
    "wavelength": 500.0,
    "conc_unit": mM,
    "signals": [0, 1, 2, 3, 4],
    "cutoff": 3,
}

mock_standard = MagicMock(spec=Standard)
mock_model = MagicMock(spec=CalibrationModel)
mock_sample = MagicMock(spec=Sample)


@pytest.fixture
def calibrator():
    return Calibrator(**dummy_calibration)


def test_initialize_models_with_no_models(calibrator):
    assert len(calibrator.models) > 0


def test_add_model(calibrator):
    new_model = calibrator.add_model(
        name="new_model",
        signal_law="s1 * a + b",
        init_value=1,
        lower_bound=-1e6,
        upper_bound=1e6,
    )
    assert new_model in calibrator.models
    assert new_model.name == "new_model"


def test_add_model_with_invalid_molecule_id(calibrator):
    with pytest.raises(AssertionError):
        calibrator.add_model(
            name="new_model",
            signal_law="anotherone * a - b",
            init_value=1,
            lower_bound=-1e-6,
            upper_bound=1e6,
        )


def test_minimal_model_init(calibrator):
    model = calibrator.add_model(
        name="new_model",
        signal_law="s1 * a + b",
    )
    pprint(model)
    assert model.name == "new_model"
    assert model.signal_law == "s1 * a + b"
    for param in model.parameters:
        assert param.init_value == 1


def test_add_model_missing_name(calibrator):
    with pytest.raises(TypeError):
        calibrator.add_model(
            signal_law="s1 * a + b", init_value=1, lower_bound=-1e-6, upper_bound=1e6
        )


def test_apply_cutoff(calibrator):
    calibrator._apply_cutoff()
    assert calibrator.concentrations == [0.2, 0.4, 0.6]
    assert calibrator.signals == [0, 1, 2]


def test_apply_cutoff_no_cutoff(calibrator):
    concs = [0.1, 0.2, 0.3, 0.4]
    signals = [1.0, 2.0, 3.0, 4.0]

    calibrator.cutoff = None
    calibrator.concentrations = concs
    calibrator.signals = signals
    calibrator._apply_cutoff()

    assert calibrator.concentrations == [0.1, 0.2, 0.3, 0.4]
    assert calibrator.signals == [1.0, 2.0, 3.0, 4.0]


def test_get_model(calibrator):
    with patch.object(calibrator, "models", [mock_model]):
        mock_model.name = "test_model"
        model = calibrator.get_model("test_model")
        assert model == mock_model

        with pytest.raises(ValueError):
            calibrator.get_model("non_existent_model")


def test_calculate_concentrations(calibrator):
    model = CalibrationModel(
        name="test_model",
        molecule_id="s1",
        signal_law="s1 * a + b",
        parameters=[
            Parameter(
                **{
                    "symbol": "a",
                    "init_value": 2.5,
                    "lower_bound": -1e6,
                    "upper_bound": 1e6,
                }
            ),
            Parameter(
                **{
                    "symbol": "b",
                    "init_value": 2,
                    "lower_bound": -1e6,
                    "upper_bound": 1e6,
                }
            ),
        ],
    )

    calibrator.models = [model]
    calibrator.fit_models()
    pprint(model)
    res = calibrator.calculate_concentrations(model=model, signals=[0.5, 1.0, 1.5])

    assert res == [0.3, 0.4, 0.5]


def test_create_standard(calibrator):
    ph = 3.3
    ld_id = "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17790"
    temperature_unit = C
    temperature = 25.1
    retention_time = 3.4
    model = calibrator.models[0]

    calibrator.fit_models()

    standard = calibrator.create_standard(
        model=model,
        ph=ph,
        ld_id=ld_id,
        temperature=temperature,
        temp_unit=temperature_unit,
        retention_time=retention_time,
    )

    assert standard.ld_id == ld_id
    assert standard.molecule_id == calibrator.molecule_id
    assert standard.molecule_name == calibrator.molecule_name
    assert standard.samples[0].concentration == 0.2
    assert standard.wavelength == 500.0
    assert standard.samples[0].conc_unit == mM
    assert standard.retention_time == retention_time
    assert standard.ph == ph
    assert standard.temperature == temperature
    assert standard.temp_unit == temperature_unit


def test_get_free_symbols(calibrator):
    eq = "s1 * a + b * 1"
    free_symbols = calibrator._get_free_symbols(eq)
    assert set(free_symbols) == set(["s1", "a", "b"])


# Updates the standard's model when both standard and molecule_id match
def test_updates_standard_model_when_ids_match(calibrator):
    old_model = mock_model
    old_model.molecule_id = calibrator.molecule_id
    calibrator.standard = old_model

    new_model = mock_model
    new_model.molecule_id = calibrator.molecule_id

    calibrator._update_model_of_standard(new_model)
    # Assert
    assert new_model == mock_model


def test_read_excel():
    cal = Calibrator.from_excel(
        path="tests/test_data/cal_test.xlsx",
        molecule_id="s1",
        molecule_name="Methanol",
        conc_unit=mM,
        wavelength=500.0,
        skip_rows=1,
    )

    assert cal.molecule_id == "s1"
    assert cal.molecule_name == "Methanol"
    assert cal.conc_unit == mM
    assert cal.wavelength == 500.0
    assert cal.concentrations == [1, 1, 2, 2, 3, 3, 4, 4]
    assert cal.signals == [22.0, 23.0, 33.0, 34.0, 44.0, 45.0, 55.0, 56.0]


def test_from_standard():
    with open("tests/test_data/abts_standard.json") as f:
        standard = Standard(**json.load(f))

    cal = Calibrator.from_standard(standard)

    assert cal.molecule_id == "s0"
    assert cal.molecule_name == "ABTS"
    assert cal.conc_unit.name == "uMole / Litre"
    assert cal.standard.temperature == 45.0
    assert cal.standard.temp_unit.name == "Celsius"
    assert cal.standard.ph == 3.5
    assert cal.standard.samples[0].concentration == 5.0
    assert cal.standard.samples[0].conc_unit.name == "uMole / Litre"
    assert cal.standard.samples[0].signal == 0.1311


def test_fit_models(calibrator):
    for model in calibrator.models:
        model.was_fitted = False
        model.calibration_range = None
    assert calibrator.models[0].was_fitted is False
    assert calibrator.models[0].calibration_range is None

    calibrator.fit_models()

    assert calibrator.models[0].was_fitted is True
    assert calibrator.models[0].calibration_range is not None
