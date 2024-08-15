# Usage

## The `Calibrator`

The `Calibrator` class is the main entry point to create and use calibration models for concentration calculation. It harbors all functionalities to load data, add calibration models, fit calibration models, calculate concentrations, and serialize serialization.  
The `Calibrator` contains a `Standard`, which harbors the data structure structuring all aspects of a fitted calibration model, measured standards, and measurement conditions.

### Initialization

The `Calibrator` can be initialized by providing the `concentrations` and respective measured `signals` as lists. Additionally, the `molecule_id` and `molecule_name` and the respective `conc_unit` need to be provided. Optionally, a `wavelength` can be provided if the signal data originates from a spectrophotometric measurement.  Furthermore, a `cutoff` can be provided to exclude signals above a certain value. 
Units are handled as predefined objects which can be imported from the `calipytion.units` module.  

```python
from calipytion import Calibrator
form calipytion.units import mM, C

calibrator = Calibrator(
    molecule_id="s0",
    molecule_name="NADH",
    conc_unit=mM,
    concentrations=[0, 1, 2, 3, 4, 5],
    signals=[1, 3, 5, 7, 9, 11],
    wavelength=420
)
```

#### From `.xlsx` file

Alternatively, the calibrator can be initialized by loading the data from a sheet of an Excel file, using the `from_excel` method. By default, the first sheet is loaded. Otherwise, the `sheet_name` can be provided, to specify the sheet to be loaded. Alongside the `path` of the file, the `molecule_id`, `molecule_name`, and `conc_unit` need to be provided. Optionally, the `wavelength` can be provided. Furthermore, using `n_header_rows` the number of rows to be skipped can be specified. By default, the first row is skipped, as it is assumed to contain the column names. 

```python
calibrator = Calibrator.from_excel(
    path="data.xlsx",
    molecule_id="s0",
    molecule_name="NADH",
    conc_unit=mM,
    wavelength=420,
    n_header_rows=1
)
```
#### From `.json` standard

Natively the `Calibrator` alongside a fitted calibration model is serialized as a `Standard` JSON file. This file can be read to reuse a calibrator, using the `from_json` method. 

```python
calibrator = Calibrator.from_json("standard.json")
```


### Adding calibration models
By default, the `Calibrator` is initialized with three polynomial calibration models, a linear, quadratic, and cubic model. These models do not include a parameter for the intercept. Thus blanked signals are assumed to be zero.  
Additional models can be added by using the `add_model` method. The method requires a `name` and a `signal_law`, describing the mathematical relationship between the signal and the concentration. Only the right side of the equation needs to be provided. The left side is assumed to be the signal. Additionally, the variable of the concentration must match the `molecule_id` provided during initialization.
Furthermore, an `initial_value`, the `lower_bound`, and the `upper_bound` can be provided for all parameters. 

```python
# delete default models
calibrator.models = []

# add a linear and quadratic model with intercept
linear = calibrator.add_model(
    name="linear",
    signal_law="a * s0 + b",
)
quadratic = calibrator.add_model(
    name="quadratic",
    signal_law="a * s0 ** 2 + b * s0 + c",
)
```

### Fitting calibration models

After specifying the calibration models, the models can be fitted to the data using the `fit_models` method. This fits all models that were added to the calibrator. After fitting, a table with fit statistics such as Akaike Information Criterion (AIC), R<sup>2</sup>, and Root Mean Squared Deviation (RMSD) is printed alongside the equation and relative parameter standard errors of each model.

```python
calibrator.fit_models()
```

### Visualizing calibration models

After fitting, the calibration models can be visualized using the `visualize` method.

### Concentration calculation

For concentration calculation, one of the fitted models can be chosen and given to the `calculate_concentrations` method. The data of unknown signals is provided as a list. By default, concentrations are only calculated if the signal is within the calibration range, which is based on the calibration data. Optionally, extrapolation can be enabled by setting `extrapolate=True`. 

```python
concentrations = calibrator.calculate_concentrations(
    model=linear,
    signals=[2, 4, 6, 8, 10]
)
```

### Serialization

Finally, the data of the calibrator can be enriched with additional information on the calibrated molecule and the measurement conditions to form a valid `Standard`. This is done by using the `create_standard` method. This method expects a `ph`, `temperature`, `temp_unit`. Optionally, the `ld_id` should be provided in the form of a PubChem ID to uniquely identify the molecule. Furthermore, the `retention_time` can be provided to further characterize the context of the calibration. 

```python
standard = calibrator.create_standard(
    ph=7.4,
    temperature=25,
    temp_unit=C,
    ld_id="https://pubchem.ncbi.nlm.nih.gov/compound/1_4-Dihydronicotinamide-adenine-dinucleotide",
    retention_time=7.53
)

# save the standard as a JSON file
with open("standard.json", "w") as f:
    f.write(standard.model_dump_json(indent=4))
```