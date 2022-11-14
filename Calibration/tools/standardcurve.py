from Calibration.core.calibration import Calibration

class StandardCurve:
    def __init__(self, calibration_data: Calibration):
        self.calibration_data = calibration_data
        self.concentration = self.calibration_data.data.standard

    def _initialize_data():
        pass


if __name__ == "__main__":
    c = Calibration()
    print(c)