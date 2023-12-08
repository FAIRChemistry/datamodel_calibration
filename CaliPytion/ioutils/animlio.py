"""Module containing functions for mapping CaliPytion to AnIML"""


from sdRDM import DataModel


try:
    animl_lib = DataModel.from_git(
        url="https://github.com/FAIRChemistry/animl-specifications",
        commit="0c51f12",
    )
except Exception as e:
    print(
        f"The following unexpected error has occured while retrieving the "
        + f"data model from GitHub: {type(e).__name__} - Is there a working "
        + f"network connection?"
    )


def map_standard_to_animl(standard: "Standard", animl_document: "AnIML") -> None:
    """Map the fields of a CaliPytion Standard object to an AnIML
    document.

    Args:
        standard (Standard): The Standard object to map.
        animl_document (AnIML): The AnIML object to map to.
    """
    # Create the SampleSet and Sample elements and set the Sample's name
    # according to the UV/Vis Technique definition document
    animl_sample = animl_document.sample_set.add_to_sample(
        name="Test Sample", sample_id="sample0000"
    )

    # Map to the Sample element
    _map_to_sample(standard=standard, sample=animl_sample)

    # Create the ExperimentStepSet object and variables to keep track of
    # the current ExperimentStep and Series and iterate over the various
    # CaliPytion Sample objects (corresponding to ExperimentSteps)
    experiment_step_set = animl_document.experiment_step_set

    current_experiment_step_id = -1
    current_series_id = 0

    for calipytion_sample in standard.samples:
        # Create the ExperimentStep for the current CaliPytion Sample
        current_experiment_step_id += 1
        new_experiment_step = animl_lib.ExperimentStep(
            name=f"Standard of c = {calipytion_sample.concentration} {calipytion_sample.conc_unit} measured at {standard.wavelength} nm",
            experiment_step_id=f"step{str(current_experiment_step_id).zfill(4)}",
        )

        # Map to the Result element of the ExperimentStep
        current_series_id = _map_sample_to_result(
            sample=calipytion_sample,
            wavelength=standard.wavelength,
            experiment_step=new_experiment_step,
            current_series_id=current_series_id,
        )

        # Map to the metadata elements Technique, Infrastructure, and
        # Method of the ExperimentStep
        _map_to_metadata_elements(
            sample=animl_sample, experiment_step=new_experiment_step
        )

        # Add the current ExperimentStep to the ExperimentStepSet
        experiment_step_set.experiment_step.append(new_experiment_step)

    # Create the final ExperimentStep for the CalibrationModel
    current_experiment_step_id += 1
    final_experiment_step = animl_lib.ExperimentStep(
        name="Calibration Model",
        experiment_step_id=f"step{str(current_experiment_step_id).zfill(4)}",
    )

    # Map the CalibrationModel to the Result element of the final
    # ExperimentStep
    _map_calibration_model_to_result(
        calibration_model=standard.model_result, experiment_step=final_experiment_step
    )

    # Add the final ExperimentStep to the ExperimentStepSet
    experiment_step_set.experiment_step.append(final_experiment_step)


def _map_to_sample(standard: "Standard", sample: "Sample") -> None:
    """Map Standard data relevant to an AnIML Sample element.

    Args:
        standard (Standard): The Standard object to map
        sample (Sample): The AnIML Sample object to map to
    """
    # Create and fill the category element for general sample
    # description parameters
    description_category = animl_lib.Category(name="Description")

    description_category.add_to_parameter(
        name="Descriptive Name",
        value=standard.name,
        parameter_type="string",
    )

    description_category.add_to_parameter(
        name="Temperature",
        value=standard.temperature,
        parameter_type="float",
        unit=animl_lib.Unit(label=str(standard.temperature_unit)),
    )

    description_category.add_to_parameter(
        name="pH",
        value=standard.ph,
        parameter_type="float",
        unit=animl_lib.Unit(label="quantity of dimension one"),
    )

    description_category.add_to_parameter(
        name="Measurement Date",
        value=str(standard.created),
        parameter_type="datetime",
    )

    sample.category.append(description_category)


def _map_sample_to_result(
    sample: "Sample",
    wavelength: float,
    experiment_step: "ExperimentStep",
    current_series_id: int,
) -> int:
    """Map the measurements contained in the Sample object to a Result
    element within an ExperimentStep object.

    Args:
        sample (Sample): A CaliPytion Sample object.
        wavelength (float): The wavelength the Standard was measured at.
        experiment_step (ExperimentStep): An AnIML ExperimentStep object.
        current_series_id (int): The variable to keep track of the current Series ID.

    Returns:
        int: Updated current_series_id.
    """
    # Create the Result object for the measurement
    result = animl_lib.Result(name="Spectrum")

    # Create the Spectrum SeriesSet according to the UV/Vis ATDD
    new_series_set = animl_lib.SeriesSet(name="Spectrum", length="1")

    # Create the custom Concentration Series, as well as the
    # Wavelength and the Intensity Series according to the UV/Vis ATDD
    # and add them to the SeriesSet.

    ### Concentration Series ###

    # Create the IndividualValueSet element and append the concentration
    # value
    concentration_value_set = animl_lib.IndividualValueSet()
    concentration_value_set.values.append(float(sample.concentration))

    # Create the Unit element
    concentration_unit = animl_lib.Unit(
        label=str(sample.conc_unit),
    )

    # Create the Series element and add both IndividualValueSet and Unit
    # to it
    concentration_series = animl_lib.Series(
        value_set=concentration_value_set,
        unit=concentration_unit,
        name="Concentration",
        dependency="independent",
        series_id=f"series{str(current_series_id).zfill(4)}",
        plot_scale="linear",
        series_type="float",
    )

    # Append the new Series to the SeriesSet and increment the id by 1
    new_series_set.series.append(concentration_series)
    current_series_id += 1

    ### Wavelength Series ###

    # Create the IndividualValueSet element and append the wavelength
    # value
    wavelength_value_set = animl_lib.IndividualValueSet()
    wavelength_value_set.values.append(float(wavelength))

    # Create the Unit element
    wavelength_unit = animl_lib.Unit(
        label="nm",
    )

    # Create the Series element and add both IndividualValueSet and Unit
    # to it
    wavelength_series = animl_lib.Series(
        value_set=wavelength_value_set,
        unit=wavelength_unit,
        name="Wavelength",
        dependency="independent",
        series_id=f"series{str(current_series_id).zfill(4)}",
        plot_scale="linear",
        series_type="float",
    )

    # Append the new Series to the SeriesSet and increment the id by 1
    new_series_set.series.append(wavelength_series)
    current_series_id += 1

    ### Intensity Series ###

    # Create the IndividualValueSet element and append the wavelength
    # value
    intensity_value_set = animl_lib.IndividualValueSet()
    intensity_value_set.values.append(float(sample.signal))

    # Create the Unit element
    intensity_unit = animl_lib.Unit(
        label="AU",
        quantity="Absorbance",
    )

    # Create the Series element and add both IndividualValueSet and Unit
    # to it
    intensity_series = animl_lib.Series(
        value_set=intensity_value_set,
        unit=intensity_unit,
        name="Intensity",
        dependency="dependent",
        series_id=f"series{str(current_series_id).zfill(4)}",
        plot_scale="linear",
        series_type="float",
    )

    # Append the new Series to the SeriesSet and increment the id by 1
    new_series_set.series.append(intensity_series)
    current_series_id += 1

    # Add the SeriesSet to the Result
    result.series_set = new_series_set

    experiment_duration_parameter = animl_lib.Parameter(
        name="Experiment Duration",
        value=0,
        parameter_type="integer",
    )

    # Add the Category to the Result
    result.add_to_category(
        name="Measurement Description",
        parameter=[experiment_duration_parameter],
    )

    # Add the Result to the ExperimentStep
    experiment_step.result.append(result)

    return current_series_id


def _map_to_metadata_elements(
    sample: "Sample", experiment_step: "ExperimentStep"
) -> None:
    """Map to various metadata elements in an ExperimentStep of an AnIML
    document.

    Args:
        sample (Sample): An AnIML sample object.
        experiment_step (ExperimentStep): An AnIML ExperimentStep object.
    """
    # ~ TECHNIQUE ELEMENT ~
    # Create the Technique reference to the UV/Vis ATDD
    experiment_step.technique = animl_lib.Technique(
        name="UV/Vis",
        uri="https://github.com/AnIML/techniques/blob/master/uv-vis.atdd",
    )

    # ~ INFRASTRUCTURE ELEMENT ~
    # Create the Infrastructure object and map the sample reference
    sample_reference = animl_lib.SampleReference(
        sample_id=sample.sample_id,
        role="measured",
        sample_purpose="consumed",
    )

    infrastructure = animl_lib.Infrastructure(
        sample_reference_set=animl_lib.SampleReferenceSet(),
    )

    infrastructure.sample_reference_set.sample_reference.append(sample_reference)

    experiment_step.infrastructure = infrastructure

    # ~ METHOD ELEMENT ~
    # Create the Method according to the UV/Vis technique definition
    method = animl_lib.Method(name="Common Method")

    measurement_type_parameter = animl_lib.Parameter(
        name="Measurment Type",
        value=(
            "Single"
            if (experiment_step.result[0].series_set.length == "1")
            else "Spectrum"
        ),
        parameter_type="string",
    )

    method.add_to_category(
        name="Instrument Settings",
        parameter=[measurement_type_parameter],
    )

    experiment_step.method = method


def _map_calibration_model_to_result(
    calibration_model: "CalibrationModel", experiment_step: "ExperimentStep"
) -> None:
    """Map the model contained in a CalibrationModel object to a Result
    element within an ExperimentStep object.

    Args:
        calibration_model (CalibrationModel): CaliPytion CalibrationModel object.
        experiment_step (ExperimentStep): An AnIML ExperimentStep object.
    """
    # Create the Result object for the model
    result = experiment_step.add_to_result(name="Calibration Model")

    # Create the Model Category
    model_category = result.add_to_category(
        name=calibration_model.name,
    )

    # Add the Model Equation as a Parameter
    model_category.add_to_parameter(
        name="Model Equation",
        value=calibration_model.equation,
        parameter_type="string",
    )

    # Add the various model Parameter objects as a Category
    parameter_category = model_category.add_to_category(name="Model Parameters")

    for parameter in calibration_model.parameters:
        parameter_category.add_to_parameter(
            name=parameter.name,
            value=float(parameter.value),
            parameter_type="float",
        )
        parameter_category.add_to_parameter(
            name="Initial value",
            value=float(parameter.init_value),
            parameter_type="float",
        )
        parameter_category.add_to_parameter(
            name="Standard error",
            value=float(parameter.standard_error),
            parameter_type="float",
        )
        parameter_category.add_to_parameter(
            name="Lower bound",
            value=float(parameter.lower_bound),
            parameter_type="float",
        )
        parameter_category.add_to_parameter(
            name="Upper bound",
            value=float(parameter.upper_bound),
            parameter_type="float",
        )

    # Add the CalibrationRange as a Category
    calibration_range = model_category.add_to_category(name="Calibration Range")

    calibration_range.add_to_parameter(
        name="Concentration lower bound",
        value=float(calibration_model.calibration_range.conc_lower),
        parameter_type="float",
    )
    calibration_range.add_to_parameter(
        name="Concentration upper bound",
        value=float(calibration_model.calibration_range.conc_upper),
        parameter_type="float",
    )
    calibration_range.add_to_parameter(
        name="Intensity lower bound",
        value=float(calibration_model.calibration_range.signal_lower),
        parameter_type="float",
    )
    calibration_range.add_to_parameter(
        name="Intensity upper bound",
        value=float(calibration_model.calibration_range.signal_upper),
        parameter_type="float",
    )

    # Add the FitStatistics as a Category
    fit_statistics = model_category.add_to_category(name="Fit statistics")

    fit_statistics.add_to_parameter(
        name="Akaike information criterion (aic)",
        value=float(calibration_model.statistics.aic),
        parameter_type="float",
    )
    fit_statistics.add_to_parameter(
        name="Bayesian information criterion (bic)",
        value=float(calibration_model.statistics.bic),
        parameter_type="float",
    )
    fit_statistics.add_to_parameter(
        name="Coefficient of determination (r^2)",
        value=float(calibration_model.statistics.r2),
        parameter_type="float",
    )
    fit_statistics.add_to_parameter(
        name="Root mean square deviation (RMSD)",
        value=float(calibration_model.statistics.rmsd),
        parameter_type="float",
    )


def id_cleanup(xml_element) -> None:
    # Check if the 'id' attribute exists and remove it
    if "id" in xml_element.attrib:
        del xml_element.attrib["id"]

    # Recursively apply to all children
    for child in xml_element:
        id_cleanup(child)
