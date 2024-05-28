from typing import List
import toml
from ..core.calibrationmodel import CalibrationModel


def read_models_from_toml(path: str) -> List[CalibrationModel]:
    models = []
    with open(path, "r") as f:
        data = toml.load(f)

    for model_data in data["model"]:
        name = model_data["name"]
        equation = model_data["equation"]
        model = CalibrationModel(name=name, equation=equation)
        models.append(model)

    return models
