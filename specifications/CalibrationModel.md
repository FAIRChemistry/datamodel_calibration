# CaliPytion

Data model for (meta-) data of standard curves and spectra for spectrophotometric data.

## Objects

### Calibration

- reactant_id
  - Type: string
  - Description: Unique identifier of the calibrated reactant.
- date_measured
  - Type: date
  - Description: Date when the calibration data was measured
- pH
  - Type: PositiveFloat
  - Description: pH of solution.
- temperature
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- temperature_unit
  - Type: TemperatureUnits
  - Description: Temperature unit.
- device
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- standard
  - Type: Standard
  - Description: Standard data of a substance.
  - Multiple: True
- spectrum
  - Type: Spectrum
  - Description: Spectrum data of a substance.
- result
  - Type: Result
  - Description: Contains calculated concentrations and information on the fitted calibration equation to calculate the concentrations.


### Device

- manufacturer
  - Type: string
  - Description: Device manufacturer.
- model
  - Type: string
  - Description: Model name of the device.
- software_version
  - Type: string
  - Description: Software version of the device.

### Standard

Description of a standard curve.

- wavelength
  - Type: float
  - Description: Detection wavelength.
- concentration
  - Type: float
  - Multiple: True
  - Description: Concentration of the reactant.
- concentration_unit
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- absorption
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration of the reactant.

### Spectrum

- concentration
  - Type: float
  - Description: Concentration of the reactant at which the spectrum was recorded.
- wavelength
  - Type: float
  - Multiple: True
  - Description: Wavelengths used for detection.
- concentration_unit
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- absorption
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to detection wavelengths.

### Result

- concentration
  - Type: float
  - Description: Calculated concentration, based on the calibration model.
  - Multiple: True
- calibration_model
  - Type: Model
  - Description: Utilized calibration model and its parameters, leading to the calculated concentrations.

### Model

- name
  - Type: string
  - Description: Name of the calibration model.
- equation
  - Type: string
  - Description: Equation of the calibration model.
- parameters
  - Type: Parameter
  - Description: Parameters of the calibration model equation.
  - Multiple: True

### Parameter

- name
  - Type: string
  - Description: Name of the parameter.
- value
  - Type: float
  - Description: Value of the parameter.

### Series

- values
  - Type: float
  - Multiple: True
  - Description: Series representing an array of value

## Enumerations

### TemperatureUnits

Values used to determine the temperature unit.

```python
CELSIUS = "C"
KELVIN = "K"
```

### ConcentrationUnits

These values are used to determine the concentration unit.

```python
MOLAR = "mole / l"
MILLIMOLAR = "mmole / l"
MICROMOLAR = "umole / l"
NANAMOLAR = "nmole / l"
GRAMLITER = "g / l"
MILLIGRAMLITER = "mg / l"
MICROGRAMLITER = "ug / l"
NANGRAMLITER = "ng / l"
```
