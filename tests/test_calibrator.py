from unittest.mock import MagicMock, patch

import pytest
from devtools import pprint

from calipytion import Calibrator
from calipytion.model import CalibrationModel, Parameter, Standard

dummy_calibration = {
    "ld-id": "https://www.ebi.ac.uk/chebi/searchId.do?chebiId=CHEBI:17790",
    "molecule_id": "s0",
    "molecule_name": "Methanol",
    "molecule_symbol": "Meth",
    "concentrations": [0.2, 0.4, 0.6, 0.8, 1.0],
    "wavelength": 500.0,
    "conc_unit": "mmol/l",
    "signals": [0,1,2,3,4],
    "cutoff": 35,
}

mock_standard = MagicMock(spec=Standard)
mock_model = MagicMock(spec=CalibrationModel)


@pytest.fixture
def calibrator():
    return Calibrator(**dummy_calibration)


def test_initialize_models_with_no_models(calibrator):
    assert len(calibrator.models) > 0


def test_add_model(calibrator):
    new_model = calibrator.add_model(
        name="new_model",
        signal_law="Meth * a + b",
        init_value=1,
        lower_bound=-1e6,
        upper_bound=1e6,
    )
    assert new_model in calibrator.models
    assert new_model.name == "new_model"


def test_add_model_with_invalid_molecule_symbol(calibrator):
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
        signal_law="Meth * a + b",
    )
    pprint(model)
    assert model.name == "new_model"
    assert model.signal_law == "Meth * a + b"
    for param in model.parameters:
        assert param.init_value == 1


def test_add_model_missing_name(calibrator):
    with pytest.raises(TypeError):
        calibrator.add_model(
            signal_law="Meth * a + b", init_value=1, lower_bound=-1e-6, upper_bound=1e6
        )


def test_apply_cutoff(calibrator):
    calibrator._apply_cutoff()
    assert calibrator.concentrations == [0.1, 0.2, 0.3]
    assert calibrator.signals == [1.0, 2.0, 3.0]


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
        molecule_symbol="Meth",
        signal_law="Meth * a + b",
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
    res = calibrator.calculate_concentrations(model=model, signals=[1.5, 2.0, 3.0])

    assert res == [0.2, 0.4, 0.6]


# example script
#
cal = Calibrator(**dummy_calibration)
lin = cal.add_model(
    name="test_model",
    signal_law="a * Meth + b",
    init_value=1,
    lower_bound=-1e6,
    upper_bound=1e6,
)

cal.fit_models()

print(cal.calculate_concentrations(model=lin, signals=[1.5, 2.0, 3.8, 4.1, 0.01]))
