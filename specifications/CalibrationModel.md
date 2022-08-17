# CalibrationDatamodel

Data model describing calibration procedures for HPLC and UV-Vis photospectrometry.

### Calibration

- __calibration_id__
  - Type: string
  - Description: Unique identifier for the calibration.
- __reactant_id__
  - Type: string
  - Description: Unique indentifier of the calibrated reactant.
- __mixture_id__
  - Type: string
  - Description: Unique indentifier of the calibrated mixture.
- __solvent_name__
  - Type: string
  - Description: Name of the used solvent.
- __solvent_pH__
  - Type: float
  - inclusiveMinimum: 0
  - inclusiveMaximum: 14
  - Description: pH of the solvent.
- __solvent_concentration__
  - Type: PositiveFloat
  - Description: Concentration of the solvent.
- __solvent_concentration_unit__
  - Type: string
  - Description: Solvent concentration unit.
- __temperature__
  - Type: PositiveFloat
  - Description: Temperature during calibration.
- __temperature_unit__
  - Type: string
  - Description: Temperature unit.
- __device__
  - Type: Device
  - Description: Device object, containing information about the analytic device.
- __standard_curve__
  - Type: StandardCurve
  - Description: Standard curve object, containing calibration data.
- __uvvis_spectrum__
  - Type: UVVisSpectrum
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
  - Type: string
  - Description: Concentration unit.

### UVVisStandardCurve [_StandardCurve_]

- __absorption*__
  - Type: Series
  - Multiple: True
  - Description: Measured absorption, corresponding to the applied concentration.

### Series

- __values*__
  - Type: float
  - Multiple: True
  - Description: Series representing an array of values

### HPLCStandardCurve [_StandardCurve_]

- __peak_area*__
  - Type: float
  - Multiple: True
  - Description: Measured peak area, corresponding to the applied concentration.

### UVVisSpectrum

- __concentration*__
  - Type: float
  - Multiple: True
  - Description: Concentration at which spectrum is recorded.
- __wavelength*__
  - Type: float
  - Multiple: True
  - Description: Wavelengths used for detection.
- __concentration_unit*__
  - Type: string
  - Description: Concentration unit.
- __absorption*__
  - Type: float
  - Multiple: True
  - Description: Measured absorption, corresponding to detection wavelengths.
