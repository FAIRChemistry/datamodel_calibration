from ..core.calibrationmodel import CalibrationModel


linear = CalibrationModel(name="linear", signal_equation="a * concentration")

quadratic = CalibrationModel(
    name="quadratic", signal_equation="a * concentration**2 + b * concentration"
)

cubic = CalibrationModel(
    name="cubic",
    signal_equation="a * concentration**3 + b * concentration**2 + c * concentration",
)
