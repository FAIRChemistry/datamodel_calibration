# Calibration Data-model

Data model handling reactant-standard data for UV-Vis photo-spectrometry.

### Calibration

- **reactant_id\***
  - Type: string
  - Description: Unique identifier of the calibrated reactant.
- **date\***
  - Type: string
  - Description: Date when the calibration data was measured
- **pH\***
  - Type: PositiveFloat
  - Description: pH of solution.
- **temperature\***
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- **temperature_unit\***
  - Type: TemperatureUnits
  - Description: Temperature unit.
- **device**
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- **data**
  - Type: Data
  - Description: Contains standard-curve and absorption-spectrum of a single reactant.

### Device

- **manufacturer**
  - Type: string
  - Description: Device manufacturer.
- **model**
  - Type: string
  - Description: Model name of the device.
- **software_version**
  - Type: string
  - Description: Software version of the device.

### Data

- **standard_curve**
  - Type: StandardCurve
  - Multiple: True
  - Description: Standard curve object, containing calibration data.
- **spectrum**
  - Type: Spectrum
  - Description: UVVisSpectrum object, containing spectrum data.

### StandardCurve

- **wavelength\***
  - Type: float
  - Description: Detection wavelength.
- **concentration\***
  - Type: float
  - Multiple: True
  - Description: Concentration of the reactant.
- **concentration_unit\***
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- **absorption\***
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration of the reactant.

### Spectrum

- **concentration\***
  - Type: float
  - Description: Concentration of the reactant at which the spectrum was recorded.
- **wavelength\***
  - Type: float
  - Multiple: True
  - Description: Wavelengths used for detection.
- **concentration_unit\***
  - Type: ConcentrationUnits
  - Description: Concentration unit.
- **absorption\***
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to detection wavelengths.

### Series

- **values\***
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
