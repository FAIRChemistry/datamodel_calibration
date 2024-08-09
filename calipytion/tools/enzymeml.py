from pyenzyme import EnzymeMLDocument, MeasurementData, SmallMolecule

from calipytion.model import CalibrationModel, Standard
from calipytion.tools.calibrator import Calibrator


def apply_standard(standard: Standard, enzmldoc: EnzymeMLDocument) -> EnzymeMLDocument:
    """Converts the measured data in concentration values for a given standard.

    Args:
        standard: The standard of a molecule.
        enzmldoc: The EnzymeMLDocument to apply the standard to.

    Returns:
        The EnzymeMLDocument with the standard applied.
    """

    try:
        small_molecule_id = get_small_molecule_id_by_ld_id(
            enzmldoc.small_molecules, standard.molecule_id
        )
    except ValueError:
        try:
            small_molecule_id = get_small_molecule_id_by_id(
                enzmldoc.small_molecules, standard.molecule_symbol
            )
        except ValueError:
            raise ValueError(f"""
            Could not find a matching small molecule in the EnzymeML document for {standard.molecule_id}
            Make sure that the molecule_id in the standard is consistent with the ld_id or id field of 
            the small_molecule in the EnzymeML document.
            """)

    calibrator = Calibrator.from_standard(standard)

    for measurement in enzmldoc.measurements:
        for measured_species in measurement.species:
            print(measured_species.species_id, small_molecule_id)
            if measured_species.species_id == small_molecule_id:
                convert_measurement(calibrator, standard.result, measured_species)
                print("converted")


def get_small_molecule_id_by_ld_id(
    small_molecules: list[SmallMolecule], molecule_id: str
) -> str:
    """Returns the `id` of the small_molecule which is consistent with the species_id in the standard
    based on the ld_id field of the species in the EnzymeML document.

    Args:
        small_molecules (list[SmallMolecule]): The list of small molecules in the EnzymeML document.
        molecule_id (str): The `molecule_id` of a `Standard`.

    Returns:
        small_molecule_id (str): The `id` of the small_molecule which is consistent with
            with the species_id in the standard

    Raises:
        ValueError: If the molecule_id is not present in the ld_id field of any species in the EnzymeML document.
    """

    for molecule in small_molecules:
        if molecule.ld_id == molecule_id:
            return molecule.id

    raise ValueError(
        f"Could not find a matching ld_id in the EnzymeML document for {molecule_id}"
    )


def get_small_molecule_id_by_id(
    small_molecules: list[SmallMolecule], molecule_symbol: str
) -> str:
    """Returns the `id` of the small_molecule which is consistent with the molecule_symbol in the standard
    based on the `id` field of the small_molecule in the EnzymeML document.

    Args:
        small_molecules (list[SmallMolecule]): The list of small molecules in the EnzymeML document.
        molecule_id (str): The `molecule_id` of a `Standard`.

    Returns:
        small_molecule_id (str): The `id` of the small_molecule which is consistent with
            with the species_id in the standard

    Raises:
        ValueError: If the molecule_id is not present in the id field of any species in the EnzymeML document.
    """

    for molecule in small_molecules:
        if molecule.id == molecule_symbol:
            return molecule.id

    raise ValueError(
        f"Could not find a matching id in the EnzymeML document for {molecule_symbol}"
    )


def convert_measurement(
    calibrator: Calibrator, model: CalibrationModel, measured_species: MeasurementData
):
    """Converts the measured data in concentration values for a given standard.

    Args:
        calibrator: The calibrator to use for the conversion.
        model: The calibration model to use for the conversion.
        measured_species: The species to convert.
    """

    signals = measured_species.data
    measured_species.data = calibrator.calculate_concentrations(model, signals)
    measured_species.data_unit = calibrator.conc_unit
