# CalibrationDatamodel

Data model describing calibration procedures for HPLC and UV-Vis photospectrometry.

### Calibration

- __reactant_id__
  - Type: string
  - Description: Unique indentifier of the calibrated reactant.
- __date__
  - Type: string
  - Description: Date when the calibration data was meeasured
- __temperature*__
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- __pH*__
  - Type: PositiveFloat
  - Description: pH of solution.
- __temperature_unit*__
  - Type: TemperatureUnits
  - Description: Temperature unit.
- __device__
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- __standard_curve__
  - Type: StandardCurve
  - Multiple: True
  - Description: Standard curve object, containing calibration data.
- __spectrum__
  - Type: Spectrum
  - Description: UVVisSpectrum object, containing spectrum data

### Device

- __device_manufacturer__
  - Type: string
  - Description: Device manufacturer.
- __device_model__
  - Type: string
  - Description: Model name of the device.
- __device_software_version__
  - Type: string
  - Description: Software version of the device.

### StandardCurve

- __wavelength*__
  - Type: float
  - Description: Detection wavelength.
- __concentration*__
  - Type: float
  - Multiple: True
  - Description: Concentration of the analyt.
- __concentration_unit*__
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- __absorption*__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration.

### Spectrum

- __concentration*__
  - Type: float
  - Multiple: True
  - Description: Concentration at which spectrum is recorded.
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
