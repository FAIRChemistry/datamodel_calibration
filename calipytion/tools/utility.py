import numpy as np


def calculate_rmsd(residuals: np.ndarray) -> float:
    """Calculates root mean square deviation between measurements and fitted model."""
    residuals = np.array(residuals)
    return float(np.sqrt(sum(residuals**2) / len(residuals)))
