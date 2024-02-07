# Welcome to CaliPytion's documentation

## About

CaliPytion is a Python tool designed for analyzing the relationship between measured signals and concentrations using various calibration models. It operates on the `Standard` data model, contining data of calibration measurements and their respective conditions, and primarily employs the `Calibrator` object. This object is adept at fitting different polynomial models to calibration data using least-squares minimization.

Key functionalities of CaliPytion include:

- __Model Fitting and Visualization__: Automatically fits different polynomial models to the data and provides interactive plots for visual comparison of these models.
- __Detailed Reporting__: Generates reports including the Akaike Information Criterion (AIC) and root-mean-square deviation (RMSD), aiding in the comparison of models based on fit quality.
- __Model Selection and Application__: Integrates the chosen model into the Standard object, using it for precise concentration calculations from measured signals. Signals outside the valid calibration are replaced with with NaN values, if model extrapolation is disabled.
- __Export and Documentation__: Allows for the export of calibration models in multiple formats like Analytical Information Markup Language (AnIML), YAML, JSON, or XML, facilitating documentation and sharing.
