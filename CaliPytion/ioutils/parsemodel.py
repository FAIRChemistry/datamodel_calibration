from typing import List
import yaml

from ..modified.model import Model


def parse_model(
        path: str = "CaliPytion/tools/models.yaml"
) -> List[Model]:
    """Parses a yaml file containing model information.

    Args:
        path (str, optional): Path to the yaml file. Defaults to "CaliPytion/tools/models.yaml".

    Returns:
        List[Model]: models parsed from yaml file
    """

    with open(path, "r") as file:
        model_infos = yaml.safe_load_all(file)

    models = []
    for model_dict in model_infos:
        for name, equation in model_dict:
            models.append(Model(equation=equation, name=name))

    return models
