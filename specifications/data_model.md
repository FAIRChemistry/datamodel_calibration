# Calibration data model

This data model structures data of standard measurements and spectra of spectroscopic measurements of a chemical species.

## Objects

### Standard

Description of a standard measurement for an analyte

- species_id
  - Type: string
  - Description: ID of the species
- name
  - Type: string
  - Description: Name of the species
- wavelength
  - Type: float
  - Description: Detection wavelength in nm
- signal_type
  - Type: SignalType
  - Description: Quantity type of the signal intensity measured
- samples
  - Type: Sample[]
  - Description: Measured signal, at a given concentration of the species
- __ph__
  - Type: float
  - Description: pH value of the solution
- __temperature__
  - Type: float
  - Description: Temperature during measurement
- __temperature_unit__
  - Type: str
  - Description: Temperature unit
- created
  - Type: datetime
  - Description: Date when the standard curve was measured
- calibration_result
  - Type: CalibrationModel
  - Description: Model which was used for concentration determination


### Sample

- concentration
  - Type: float
  - Description: Concentration of the species
- conc_unit
    - Type: str
    - Description: Concentration unit
- signal
    - Type: float
    - Description: Measured signals at a given concentration of the species

### CalibrationModel

- name
  - Type: string
  - Description: Name of the calibration model
- equation
  - Type: string
  - Description: Equation for the measured signal
- parameters
  - Type: Parameter[]
  - Description: Parameters of the calibration equation
- was_fitted
  - Type: boolean
  - Description: Indicates if the model was fitted to the data
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
- standard_error
  - Type: float
  - Description: Standard error of the parameter
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
