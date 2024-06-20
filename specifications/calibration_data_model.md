# Calibration Data Model

This data model structures data of standard measurements and spectra of spectroscopic measurements of a molecule.

## Objects

### Standard

The Standard describes the calibration data and the calibration model. The calibration data consists of the measured signal intensities at different concentrations of the molecule. The calibration model describes the relationship between the signal intensity and the concentration of the molecule. Furthermore, the valid concentration range defined by the underlying data is given.

- **molecule_id**
  - Type: string
  - Description: URI of the molecule (e.g. PubChem or ChEBI).
- **molecule_symbol**
  - Type: string
  - Description: Symbol representing the molecule in the calibration equation.
- **ph**
  - Type: float
  - Description: pH value of the solution.
- **temperature**
  - Type: float
  - Description: Temperature during calibration.
- **temp_unit**
  - Type: str
  - Description: Temperature unit.
- wavelength
  - Type: float
  - Description: Detection wavelength in nm
- molecule_name
  - Type: string
  - Description: Name of the molecule
- signal_type
  - Type: SignalType
  - Description: Quantity type of the signal intensity measured
- samples
  - Type: Sample[]
  - Description: Measured signal, at a given concentration of the molecule
- created
  - Type: datetime
  - Description: Date when this file was created
- result
  - Type: CalibrationModel
  - Description: The model which was used for concentration determination

### Sample

The Sample describes one measured signal-concentration pair.

- **concentration**
  - Type: float
  - Description: Concentration of the molecule.
- **conc_unit**
  - Type: str
  - Description: Concentration unit
- **signal**
  - Type: float
  - Description: Measured signals at a given concentration of the molecule

### CalibrationModel

The CalibrationModel describes the calibration model which was fitted to the calibration data. The calibration model consists of the signal law and harbors the parameters of the calibration equation. The calibration range defines the concentration and signal bounds in which the calibration model is valid.

- **name**
  - Type: string
  - Description: Name of the calibration model
- molecule_id
  - Type: string
  - Description: ID of the molecule like ChEBI ID.
- signal_law
  - Type: string
  - Description: Law describing the signal intensity as a function of the concentration
- parameters
  - Type: Parameter[]
  - Description: Parameters of the calibration equation
- molecule_symbol
  - Type: string
  - Description: Symbol representing the molecule in the signal law
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

Defines the concentration and signal bounds in which the calibration model is valid.

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

Contains the fit statistics of the calibration model for the calibration data.

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

The Parameter describes the parameters of the calibration equation.

- symbol
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
  - Description: Lower bound of the parameter prior to fitting
- upper_bound
  - Type: float
  - Description: Upper bound of the parameter prior to fitting

## Enumerations

### SignalType

Allowed quantity types of the measured signal intensities.

```python
ABSORBANCE = "absorbance"
TRANSMITTANCE = "transmittance"
REFLECTANCE = "reflectance"
```
