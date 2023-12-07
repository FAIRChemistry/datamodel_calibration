import numpy as np
from datetime import datetime

from CaliPytion.core import Calibrator, Standard


def random(xs):
    return xs + np.random.normal(0, 0.03, 1)


SLOPE = 0.014
CONC = np.linspace(0, 200, 11)
ABSO = CONC * SLOPE


def generate_standard():
    # Generate standard
    standard = Standard(
        species_id="s0",
        name="ABTS",
        wavelength=340,
        ph=2,
        temperature=25,
        temperature_unit="C",
        created=datetime.now(),
    )

    # Add samples with noise
    for conc, abso in zip(CONC, ABSO):
        standard.add_to_samples(
            concentration=conc,
            conc_unit="umol / l",
            signal=random(abso),
        )
        standard.add_to_samples(
            concentration=conc,
            conc_unit="umol / l",
            signal=random(abso),
        )
        standard.add_to_samples(
            concentration=conc,
            conc_unit="umol / l",
            signal=random(abso),
        )

    # initialize calibrator
    calibrator = Calibrator.from_standard(standard, cutoff=2.5)

    calibrator.add_to_models(
        name="exponential",
        equation="a * exp(b * concentration) = signal",
    )

    # Fit all defined models
    calibrator.fit_models()

    linear = calibrator.get_model("linear")

    # Return Standard
    return calibrator.save_model(linear)


if __name__ == "__main__":
    standard = generate_standard()
    standard.to_animl()
