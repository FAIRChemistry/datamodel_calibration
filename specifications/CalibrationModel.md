# Calibration data-model

Data model handling reactant-standard data for UV-Vis photo-spectrometry.

### Calibration

- __reactant_id__
  - Type: string
  - Description: Unique identifier of the calibrated reactant.
- __date__
  - Type: string
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

- __standard__
  - Type: Standard
  - Description: Standard data of a substance.
- __spectrum__
  - Type: Spectrum
  - Description: Spectrum data of a substance.

### Standard

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
MOLAR = "M"
MILLIMOLAR = "mM"
MICROMOLAR = "uM"
NANOMOLAR = "nM"
```
