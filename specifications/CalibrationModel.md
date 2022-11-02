# CalibrationDatamodel

Data model handling reactant-standard data for UV-Vis photospectrometry.

### Calibration

- __reactant_id*__
  - Type: string
  - Description: Unique indentifier of the calibrated reactant.
- __date*__
  - Type: string
  - Description: Date when the calibration data was meeasured
- __pH*__
  - Type: PositiveFloat
  - Description: pH of solution.
- __temperature*__
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- __temperature_unit*__
  - Type: TemperatureUnits
  - Description: Temperature unit.
- __device__
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- __data__
  - Type: Data
  - Description: Contains standard-curve and absorption-spectrum of a single reactant.

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

### Data

- __standard_curve__
  - Type: StandardCurve
  - Multiple: True
  - Description: Standard curve object, containing calibration data.
- __spectrum__
  - Type: Spectrum
  - Description: UVVisSpectrum object, containing spectrum data.

### StandardCurve

- __wavelength*__
  - Type: float
  - Description: Detection wavelength.
- __concentration*__
  - Type: float
  - Multiple: True
  - Description: Concentration of the reactant.
- __concentration_unit*__
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- __absorption*__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration of the reactant.

### Spectrum

- __concentration*__
  - Type: float
  - Description: Concentration of  the reactant at which the spectrum was recorded.
- __wavelength*__
  - Type: float
  - Multiple: True
  - Description: Wavelengths used for detection.
- __concentration_unit*__
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- __absorption*__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to detection wavelengths.

### Series

- __values*__
  - Type: float
  - Multiple: True
  - Description: Series representing an array of value

#### TemperatureUnits

These values are used to determine the temperature unit.

```python
CELSIUS = "C"
KELVIN = "K"
```
#### ConcentrationUnits

These values are used to determine the concentration unit.

```python
MOLAR = "M"
MILLIMOLAR = "mM"
MICROMOLAR = "uM"
NANOMOLAR = "nM"
```
