# CaliPytion

Data model for (meta-) data of standard curves and spectra for spectrophotometric data.
### Calibration

- __reactant_id__
  - Type: string
  - Description: Unique identifier of the calibrated reactant.
- __date__
  - Type: date
  - Description: Date when the calibration data was measured
- __pH__
  - Type: PositiveFloat
  - Description: pH of solution.
- __temperature__
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- __temperature_unit__
  - Type: TemperatureUnits
  - Description: Temperature unit.
- __device__
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- __standard__
  - Type: Standard
  - Description: Standard data of a substance.
  - Multiple: True
- __spectrum__
  - Type: Spectrum
  - Description: Spectrum data of a substance.
- __result__
  - Type: Result
  - Description: Contains calculated concentrations and information on the fitted calibration equation to calculate the concentrations.


### Device

- __manufacturer__
  - Type: string
  - Description: Device manufacturer.
- __model__
  - Type: string
  - Description: Model name of the device.
- __software_version__
  - Type: string
  - Description: Software version of the device.

### Standard

Description of a standard curve.

- __wavelength__
  - Type: float
  - Description: Detection wavelength.
- __concentration__
  - Type: float
  - Multiple: True
  - Description: Concentration of the reactant.
- __concentration_unit__
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- __absorption__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration of the reactant.

### Spectrum

- __concentration__
  - Type: float
  - Description: Concentration of the reactant at which the spectrum was recorded.
- __wavelength__
  - Type: float
  - Multiple: True
  - Description: Wavelengths used for detection.
- __concentration_unit__
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- __absorption__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to detection wavelengths.

### Result

- __concentration__
  - Type: float
  - Description: Calculated concentration, based on the calibration model.
  - Multiple: True
- __calibration_model__
  - Type: Model
  - Description: Utilized calibration model and its parameters, leading to the calculated concentrations.

### Model

- __name__
  - Type: string
  - Description: Name of the calibration model.
- __equation__
  - Type: string
  - Description: Equation of the calibration model.
- __parameters__
  - Type: Parameter
  - Description: Parameters of the calibration model equation.
  - Multiple: True

### Parameter

- __name__
  - Type: string
  - Description: Name of the parameter.
- __value__
  - Type: float
  - Description: Value of the parameter.

### Series

- __values__
  - Type: float
  - Multiple: True
  - Description: Series representing an array of value

#### TemperatureUnits

Values used to determine the temperature unit.

```python
CELSIUS = "C"
KELVIN = "K"
```

#### ConcentrationUnits

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
