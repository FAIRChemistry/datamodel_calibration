from pyenzyme import SmallMolecule

# from calipytion.tools.calibrator import Calibrator


# def apply_to_enzymeml(
#     calibrators: list[Calibrator] | Calibrator,
#     enzmldoc: EnzymeMLDocument,
#     extrapolate: bool = False,
# ):
#     """Converts the measured data in concentration values for a given standard.

#     Args:
#         calibrators: The calibrators to use for the conversion.
#         enzmldoc: The EnzymeMLDocument to apply the standard to.
#         extrapolate: If True, the calibration models will extrapolate if the signals
#             are outside the calibration range.
#     """

#     if not isinstance(calibrators, list):
#         calibrators = [calibrators]

#     for calibrator in calibrators:
#         assert calibrator.standard.result is not None, f"""
#         The calibrator for {calibrator.standard.molecule_id} does not have a result.
#         Call the `create_standard` method on the calibrator before applying it to the EnzymeML document.
#         """

#         try:
#             small_molecule_id = get_small_molecule_id_by_ld_id(
#                 enzmldoc.small_molecules, calibrator.ld_id
#             )
#         except ValueError:
#             try:
#                 small_molecule_id = get_small_molecule_id_by_id(
#                     enzmldoc.small_molecules, calibrator.molecule_id
#                 )
#             except ValueError:
#                 raise ValueError(f"""
#                 Could not find a matching small molecule in the EnzymeML document for {calibrator.molecule_id}
#                 Make sure that the molecule_id in the standard is consistent with the ld_id or id field of
#                 the small_molecule in the EnzymeML document.
#                 """)

#         for measurement in enzmldoc.measurements:
#             for measured_species in measurement.species:
#                 if measured_species.species_id == small_molecule_id:
#                     convert_measurement(
#                         calibrator,
#                         calibrator.standard.result,
#                         measured_species,
#                         extrapolate,
#                     )


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
    small_molecules: list[SmallMolecule], molecule_id: str
) -> str:
    """Returns the `id` of the small_molecule which is consistent with the molecule_id in the standard
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
        if molecule.id == molecule_id:
            return molecule.id

    raise ValueError(
        f"Could not find a matching id in the EnzymeML document for {molecule_id}"
    )


# def convert_measurement(
#     calibrator: Calibrator,
#     model: CalibrationModel,
#     measured_species: MeasurementData,
#     extrapolate: bool,
# ):
#     """Converts the measured data in concentration values for a given standard.

#     Args:
#         calibrator: The calibrator to use for the conversion.
#         model: The calibration model to use for the conversion.
#         measured_species: The species to convert.
#     """

#     # assert units are the same
#     assert measured_species.data_unit.__str__() == calibrator.conc_unit.__str__(), f"""
#     The unit of the measured data ({measured_species.data_unit.name}) is not
#     the same as the unit of the calibration model ({calibrator.conc_unit.name}).
#     """

#     signals = measured_species.data
#     measured_species.data = calibrator.calculate_concentrations(
#         model, signals, extrapolate
#     )
#     measured_species.data_type = DataTypes.CONCENTRATION
