# Calibration Data Model

This data model structures data of standard measurements and spectra of spectroscopic measurements of a chemical species.

## Objects

### Standard

Description of a standard measurement for an analyte

- **name**
  - Type: string
  - Description: Name of the species
- **ph**
  - Type: float
  - Description: pH value of the solution
- **temperature**
  - Type: float
  - Description: Temperature during measurement
- **temperature_unit**
  - Type: str
  - Description: Temperature unit
- wavelength
  - Type: float
  - Description: Detection wavelength in nm
- signal_type
  - Type: SignalType
  - Description: Quantity type of the signal intensity measured
- samples
  - Type: Sample[]
  - Description: Measured signal, at a given concentration of the species
- created
  - Type: datetime
  - Description: Date when the this file was created
- modified
  - Type: datetime
  - Description: Date when the this file was last modified
- calibration_result
  - Type: CalibrationModel
  - Description: The model which was used for concentration determination

### Sample

- **species_id**
  - Type: string
  - Description: ID of the species
- **concentration**
  - Type: float
  - Description: Concentration of the species
- **unit**
  - Type: str
  - Description: Concentration unit
- **signal**
  - Type: float
  - Description: Measured signals at a given concentration of the species

### CalibrationModel

- **name**
  - Type: string
  - Description: Name of the calibration model
- **signal_law**
  - Type: string
  - Description: Law describing the signal intensity as a function of the concentration
- parameters
  - Type: Parameter[]
  - Description: Parameters of the calibration equation
- was_fitted
  - Type: boolean
  - Description: Indicates if the model was fitted to the data
  - default: False
- calibration_range
  - Type: CalibrationRange
  - Description: Concentration and signal bounds in which the calibration model is valid.
- statistics
  - Type: FitStatistics
  - Description: Fit statistics of the calibration model

### CalibrationRange

- conc_lower
  - Type: float
  - Description: Lower concentration bound of the model
- conc_upper
  - Type: float
  - Description: Upper concentration bound of the model
- signal_lower
  - Type: float
  - Description: Lower signal bound of the model
- signal_upper
  - Type: float
  - Description: Upper signal bound of the model

### FitStatistics

- aic
  - Type: float
  - Description: Akaike information criterion
- bic
  - Type: float
  - Description: Bayesian information criterion
- r2
  - Type: float
  - Description: Coefficient of determination
- rmsd
  - Type: float
  - Description: Root mean square deviation

### Parameter

- name
  - Type: string
  - Description: Name of the parameter
- value
  - Type: float
  - Description: Value of the parameter
- init_value
  - Type: float
  - Description: Initial value of the parameter
- stderr
  - Type: float
  - Description: 1-sigma standard error of the parameter
- lower_bound
  - Type: float
  - Description: Lower bound of the parameter
- upper_bound
  - Type: float
  - Description: Upper bound of the parameter

## Enumerations

### SignalType

Allowed quantity types of the measured signal intensities.

```python
ABSORBANCE = "Absorbance"
TRANSMITTANCE = "Transmittance"
REFLECTANCE = "Reflectance"
```
