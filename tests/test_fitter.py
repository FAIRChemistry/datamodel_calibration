import numpy as np
import pytest
from lmfit import Parameters

from calipytion.model import FitStatistics, Parameter
from calipytion.tools.fitter import Fitter

# Mock data for testing
equation = "a * x + b"
indep_var = "x"
params = [
    Parameter(symbol="a", init_value=1, lower_bound=-10, upper_bound=10),
    Parameter(symbol="b", init_value=1, lower_bound=-10, upper_bound=10),
]


@pytest.fixture
def fitter() -> Fitter:
    return Fitter(equation, indep_var, params)


def test_fit(fitter):
    x = np.array([0, 1, 2, 3, 4])
    y = np.array([2, 4, 6, 8, 10])
    dep_var_name = "x"
    fit_stats = fitter.fit(y, x, dep_var_name)
    assert fitter.lmfit_result.success
    assert isinstance(fit_stats, FitStatistics)
    assert fit_stats.r2 > 0.99
    assert round(fitter.params[0].value) == pytest.approx(2, abs=0.1)
    assert fitter.params[1].value == pytest.approx(2, abs=0.1)


def test_calculate_roots(fitter):
    y = np.array([2, 4, 6, 8, 10])
    lower_bound = 0
    upper_bound = 10
    roots, interval = fitter.calculate_roots(
        y, lower_bound, upper_bound, extrapolate=False
    )
    assert interval == [0, 10]
    assert isinstance(roots, np.ndarray)
    assert len(roots) == len(y)


def test_from_calibration_model():
    from calipytion.model import CalibrationModel

    calibration_model = CalibrationModel(
        signal_law=equation,
        name="linear_model",
        molecule_id=indep_var,
        parameters=params,
    )
    fitter_instance = Fitter.from_calibration_model(calibration_model)
    assert isinstance(fitter_instance, Fitter)
    assert fitter_instance.equation == equation
    assert fitter_instance.indep_var == indep_var


def test_prepare_params(fitter):
    lm_params = fitter._prepare_params()
    assert isinstance(lm_params, Parameters)
    assert lm_params["a"].value == 1.0
    assert lm_params["b"].value == 1.0


def test_get_model_callable(fitter):
    callable_ = fitter._get_model_callable()
    assert callable_(8, 2, 2) == 8 * 2 + 2  # Simple test for the equation "a * x + b"


def test_root_eq_correct_eval(fitter):
    root_eq = fitter._get_root_eq()
    fitter.fit(np.array([2, 4, 6]), np.array([0, 1, 2]), "x")

    # Test if the root equation is correctly evaluated
    assert root_eq(x=2, a=2, b=2, SIGNAL_PLACEHOLDER=6) == pytest.approx(0, abs=0.1)


def test_update_result_params(fitter):
    # Mock lmfit result
    params = Parameters()
    params.add("a", value=11.0)
    params.add("b", value=22.0)

    fitter.lmfit_params = params
    fitter._update_result_params()

    assert fitter.params[0].value == pytest.approx(11.0, abs=0.001)
    assert fitter.params[1].value == pytest.approx(22.0, abs=0.001)


def test_extract_fit_statistics(fitter):
    # Mock lmfit result
    class MockResult:
        def __init__(self):
            self.aic = 1.0
            self.bic = 2.0
            self.rsquared = 0.9995
            self.residual = np.array([0.1, 0.2, 0.3])
            self.success = True

    mock_result = MockResult()
    stats = fitter.extract_fit_statistics(mock_result)
    rmsd = np.sqrt(np.mean(np.array([0.1, 0.2, 0.3]) ** 2))
    assert isinstance(stats, FitStatistics)
    assert stats.aic == 1.0
    assert stats.bic == 2.0
    assert stats.r2 == 0.9995
    assert stats.rmsd == pytest.approx(rmsd, abs=0.0001)
