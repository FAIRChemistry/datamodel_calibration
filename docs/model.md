---
hide:
    - navigation
---

# Calibration Standard Data Model

This page provides comprehensive information about the structure and components of the data model, including detailed descriptions of the types and their properties, information on enumerations, and an overview of the ontologies used and their associated prefixes. Below, you will find a graph that visually represents the overall structure of the data model.

??? quote "Graph"
    ``` mermaid
    flowchart TB
        standard(Standard)
        sample(Sample)
        calibrationmodel(CalibrationModel)
        calibrationrange(CalibrationRange)
        fitstatistics(FitStatistics)
        parameter(Parameter)
        unitdefinition(UnitDefinition)
        baseunit(BaseUnit)
        signaltype(SignalType)
        unittype(UnitType)
        standard(Standard) --> unitdefinition(UnitDefinition)
        standard(Standard) --> signaltype(SignalType)
        standard(Standard) --> sample(Sample)
        standard(Standard) --> calibrationmodel(CalibrationModel)
        sample(Sample) --> unitdefinition(UnitDefinition)
        calibrationmodel(CalibrationModel) --> parameter(Parameter)
        calibrationmodel(CalibrationModel) --> calibrationrange(CalibrationRange)
        calibrationmodel(CalibrationModel) --> fitstatistics(FitStatistics)
        unitdefinition(UnitDefinition) --> baseunit(BaseUnit)
        baseunit(BaseUnit) --> unittype(UnitType)

        click standard "#standard" "Go to Standard"
        click sample "#sample" "Go to Sample"
        click calibrationmodel "#calibrationmodel" "Go to CalibrationModel"
        click calibrationrange "#calibrationrange" "Go to CalibrationRange"
        click fitstatistics "#fitstatistics" "Go to FitStatistics"
        click parameter "#parameter" "Go to Parameter"
        click unitdefinition "#unitdefinition" "Go to UnitDefinition"
        click baseunit "#baseunit" "Go to BaseUnit"
        click signaltype "#signaltype" "Go to SignalType"
        click unittype "#unittype" "Go to UnitType"
    ```


## Types


### Standard
The Standard describes the calibration data and the calibration model. The calibration data consists of the measured signal intensities at different concentrations of the molecule. The calibration model describes the relationship between the signal intensity and the concentration of the molecule. Furthermore, the valid concentration range defined by the underlying data is given.

__molecule_id__* `string`

- URI of the molecule (e.g. PubChem or ChEBI).


__molecule_symbol__* `string`

- Symbol representing the molecule in the calibration equation.


__ph__* `float`

- pH value of the solution.


__temperature__* `float`

- Temperature during calibration.


__temp_unit__* [`UnitDefinition`](#unitdefinition)

- Temperature unit.


__wavelength__ `float`

- Detection wavelength in nm


__molecule_name__ `string`

- Name of the molecule


__signal_type__ [`SignalType`](#signaltype)

- Quantity type of the signal intensity measured


__samples__ [`list[Sample]`](#sample)

- Measured signal, at a given concentration of the molecule


__created__ `string`

- Date when this file was created


__result__ [`CalibrationModel`](#calibrationmodel)

- The model which was used for concentration determination


------

### Sample
The Sample describes one measured signal-concentration pair.

__concentration__* `float`

- Concentration of the molecule.


__conc_unit__* [`UnitDefinition`](#unitdefinition)

- Concentration unit


__signal__* `float`

- Measured signals at a given concentration of the molecule


------

### CalibrationModel
The CalibrationModel describes the calibration model which was fitted to the calibration data. The calibration model consists of the signal law and harbors the parameters of the calibration equation. The calibration range defines the concentration and signal bounds in which the calibration model is valid.

__name__* `string`

- Name of the calibration model


__molecule_id__ `string`

- ID of the molecule like ChEBI ID.


__signal_law__ `string`

- Law describing the signal intensity as a function of the concentration


__parameters__ [`list[Parameter]`](#parameter)

- Parameters of the calibration equation


__molecule_symbol__ `string`

- Symbol representing the molecule in the signal law


__was_fitted__ `boolean`

- Indicates if the model was fitted to the data

- `Default`: false

__calibration_range__ [`CalibrationRange`](#calibrationrange)

- Concentration and signal bounds in which the calibration model is valid.


__statistics__ [`FitStatistics`](#fitstatistics)

- Fit statistics of the calibration model


------

### CalibrationRange
Defines the concentration and signal bounds in which the calibration model is valid.

__conc_lower__ `float`

- Lower concentration bound of the model


__conc_upper__ `float`

- Upper concentration bound of the model


__signal_lower__ `float`

- Lower signal bound of the model


__signal_upper__ `float`

- Upper signal bound of the model


------

### FitStatistics
Contains the fit statistics of the calibration model for the calibration data.

__aic__ `float`

- Akaike information criterion


__bic__ `float`

- Bayesian information criterion


__r2__ `float`

- Coefficient of determination


__rmsd__ `float`

- Root mean square deviation


------

### Parameter
The Parameter describes the parameters of the calibration equation.

__symbol__ `string`

- Name of the parameter


__value__ `float`

- Value of the parameter


__init_value__ `float`

- Initial value of the parameter


__stderr__ `float`

- 1-sigma standard error of the parameter


__lower_bound__ `float`

- Lower bound of the parameter prior to fitting


__upper_bound__ `float`

- Upper bound of the parameter prior to fitting


------

### UnitDefinition
Represents a unit definition that is based on the SI unit system.

__id__ `string`

- Unique identifier of the unit definition.


__name__ `string`

- Common name of the unit definition.


__base_units__ [`list[BaseUnit]`](#baseunit)

- Base units that define the unit.


------

### BaseUnit
Represents a base unit in the unit definition.

__kind__* [`UnitType`](#unittype)

- Kind of the base unit (e.g., meter, kilogram, second).


__exponent__* `integer`

- Exponent of the base unit in the unit definition.


__multiplier__ `float`

- Multiplier of the base unit in the unit definition.


__scale__ `float`

- Scale of the base unit in the unit definition.


## Enumerations

### SignalType

| Alias | Value |
|-------|-------|
| `ABSORBANCE` | absorbance |
| `REFLECTANCE` | reflectance |
| `TRANSMITTANCE` | transmittance |

### UnitType

| Alias | Value |
|-------|-------|
| `AMPERE` | ampere |
| `AVOGADRO` | avogadro |
| `BECQUEREL` | becquerel |
| `CANDELA` | candela |
| `CELSIUS` | celsius |
| `COULOMB` | coulomb |
| `DIMENSIONLESS` | dimensionless |
| `FARAD` | farad |
| `GRAM` | gram |
| `GRAY` | gray |
| `HENRY` | henry |
| `HERTZ` | hertz |
| `ITEM` | item |
| `JOULE` | joule |
| `KATAL` | katal |
| `KELVIN` | kelvin |
| `KILOGRAM` | kilogram |
| `LITRE` | litre |
| `LUMEN` | lumen |
| `LUX` | lux |
| `METRE` | metre |
| `MOLE` | mole |
| `NEWTON` | newton |
| `OHM` | ohm |
| `PASCAL` | pascal |
| `RADIAN` | radian |
| `SECOND` | second |
| `SIEMENS` | siemens |
| `SIEVERT` | sievert |
| `STERADIAN` | steradian |
| `TESLA` | tesla |
| `VOLT` | volt |
| `WATT` | watt |
| `WEBER` | weber |