from ..core.calibrationmodel import CalibrationModel


linear = CalibrationModel(name="linear", equation="a * concentration = signal")

quadratic = CalibrationModel(
    name="quadratic", equation="a * concentration**2 + b * concentration = signal"
)

cubic = CalibrationModel(
    name="cubic",
    equation="a * concentration**3 + b * concentration**2 + c * concentration = signal",
)
