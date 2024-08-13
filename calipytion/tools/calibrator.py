from __future__ import annotations

import logging
from typing import Any, Optional

import numpy as np
import plotly.express as px
import sympy as sp
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from pydantic import BaseModel, Field, ValidationInfo, field_validator
from rich.console import Console
from rich.table import Table

from calipytion.model import (
    CalibrationModel,
    CalibrationRange,
    Standard,
    UnitDefinition,
)
from calipytion.tools.fitter import Fitter
from calipytion.units import C

LOGGER = logging.getLogger(__name__)


class Calibrator(BaseModel):
    """
    Class to handle the calibration process and including creation, fitting, comparison,
    visualization, and selection of calibration models.
    """

    molecule_id: str = Field(
        description="Unique identifier of the given object.",
    )

    molecule_name: str = Field(
        description="Name of the molecule",
    )

    concentrations: list[float] = Field(
        description="Concentrations of the standard",
    )

    wavelength: float | None = Field(
        description="Wavelength of the measurement",
        default=None,
    )

    conc_unit: UnitDefinition = Field(
        description="Concentration unit",
    )

    signals: list[float] = Field(
        description="Measured signals, corresponding to the concentrations",
    )

    models: list[CalibrationModel] = Field(
        description="Models used for fitting", default=[], validate_default=True
    )

    cutoff: float | None = Field(
        default=None,
        description=(
            "Upper cutoff value for the measured signal. All signals above this value"
            " will be ignored during calibration"
        ),
    )

    standard: Standard | None = Field(
        default=None,
        description="Result oriented object, representing the data and the chosen model.",
    )

    @field_validator("models")
    @classmethod
    def initialize_models(cls, v: list[CalibrationModel], info: ValidationInfo):
        """
        Loads the default models if no models are provided and initializes the models
        with the according 'molecule_id'.
        """
        if not v:
            molecule_id = info.data["molecule_id"]
            from calipytion.tools.equations import (
                cubic_model,
                linear_model,
                quadratic_model,
            )

            for model in [linear_model, quadratic_model, cubic_model]:
                model.signal_law = model.signal_law.replace(
                    "concentration", molecule_id
                )
                model.molecule_id = molecule_id

            v = [linear_model, quadratic_model, cubic_model]

            return v

        return v

    def model_post_init(self, __context: Any) -> None:
        self._apply_cutoff()

    def add_model(
        self,
        name: str,
        signal_law: str,
        init_value: float = 1,
        lower_bound: float = -1e-6,
        upper_bound: float = 1e6,
    ) -> CalibrationModel:
        """Add a model to the list of models used for calibration."""

        assert (
            self.molecule_id in signal_law
        ), f"Equation must contain the symbol of the molecule to be calibrated ('{self.molecule_id}')"

        model = CalibrationModel(
            molecule_id=self.molecule_id,
            name=name,
            signal_law=signal_law,
        )

        for symbol in self._get_free_symbols(signal_law):
            if symbol == self.molecule_id:
                model.molecule_id = symbol
                continue

            model.add_to_parameters(
                symbol=symbol,
                init_value=init_value,
                lower_bound=lower_bound,
                upper_bound=upper_bound,
            )

        self.models.append(model)

        return model

    def _get_free_symbols(self, equation: str) -> list[str]:
        """Gets the free symbols from a sympy equation and converts them to strings."""

        sp_eq = sp.sympify(equation)
        symbols = list(sp_eq.free_symbols)

        return [str(symbol) for symbol in symbols]

    def _apply_cutoff(self):
        """Applies the cutoff value to the signals and concentrations."""

        if self.cutoff:
            below_cutoff_idx = [
                idx for idx, signal in enumerate(self.signals) if signal < self.cutoff
            ]

            self.concentrations = [self.concentrations[idx] for idx in below_cutoff_idx]
            self.signals = [self.signals[idx] for idx in below_cutoff_idx]

    def get_model(self, model_name: str) -> CalibrationModel:
        """Returns a model by its name."""

        for model in self.models:
            if model.name == model_name:
                return model

        raise ValueError(f"Model '{model_name}' not found")

    def calculate_concentrations(
        self,
        model: CalibrationModel | str,
        signals: list[float],
        extrapolate: bool = False,
    ) -> list[float]:
        """Calculates the concentration from a given signal using a calibration model.

        When calculating the concentration, the model is used to calculate the roots of the
        equation for the given signals. The model is parameterized by previous fitting using the
        `fit_models` method.
        By default extrapolation is disabled, meaning that the concentration is only calculated
        within the calibration range of the model. If extrapolation is enabled, the concentration
        can be calculated outside the calibration range. Be aware that the results might be
        unreliable.

        Args:
            model (CalibrationModel | str): The model object or name which should be used.
            signals (list[float]): The signals for which the concentration should be calculated.
            extrapolate (bool, optional): Whether to extrapolate the concentration outside the
                calibration range. Defaults to False.

        Returns:
            list[float]: The calculated concentrations.
        """
        if not isinstance(model, CalibrationModel):
            model = self.get_model(model)

        np_signals = np.array(signals)

        lower_bond = min(self.concentrations)
        upper_bond = max(self.concentrations)

        if extrapolate:
            cal_range = upper_bond - lower_bond
            lower_bond -= cal_range
            upper_bond += cal_range

            LOGGER.warn(
                f"⚠️ Extrapolation is enabled. Allowing extrapolation in range between "
                f"{lower_bond:.2f} and {upper_bond:.2f} {self.conc_unit}."
            )

        cal_model = Fitter.from_calibration_model(model)
        concs = cal_model.calculate_roots(
            y=np_signals,
            lower_bond=lower_bond,
            upper_bond=upper_bond,
            extrapolate=extrapolate,
        )

        # give warning if any concentration is nan
        if np.isnan(concs).any() and not extrapolate:
            LOGGER.warning(
                "⚠️ Some concentrations could not be calculated and were replaced with nan "
                "values, since the provided signal is outside the calibration range. "
                "To calculate the concentration outside the calibration range, set "
                "'extrapolate=True'."
            )

        # Update or create standard object based on used model
        if self.standard:
            self._update_model_of_standard(model)

        return concs.tolist()

    def _update_model_of_standard(self, model: CalibrationModel) -> None:
        """Updates the model of the standard object with the given model."""

        assert self.standard, "No standard object found."
        assert (
            self.molecule_id == self.standard.molecule_id
        ), "The molecule id of the Calibrator and the Standard object must be the same."

        self.standard.result = model

    @classmethod
    def from_standard(
        cls,
        standard: Standard,
        cutoff: float | None = None,
    ) -> Calibrator:
        """Initialize the Calibrator object from a Standard object.

        Args:
            standard (Standard): The Standard object to be used for calibration.
            cutoff (float | None, optional): Whether to apply a cutoff value to the signals.
                This filters out all signals and corresponding concentration above the
                cutoff value. Defaults to None.

        Raises:
            ValueError: If the number of concentrations and signals are not the same.
            ValueError: If all samples do not have the same concentration unit.

        Returns:
            Calibrator: The Calibrator object.
        """

        # get concentrations and corresponding signals as lists
        concs = [sample.concentration for sample in standard.samples]
        signals = [sample.signal for sample in standard.samples]
        if not len(concs) == len(signals):
            raise ValueError("Number of concentrations and signals must be the same")

        # verify that all samples have the same concentration unit
        if not all(
            [
                sample.conc_unit == standard.samples[0].conc_unit
                for sample in standard.samples
            ]
        ):
            raise ValueError("All samples must have the same concentration unit")
        conc_unit = standard.samples[0].conc_unit

        return cls(
            molecule_id=standard.molecule_id,
            molecule_name=standard.molecule_name,
            concentrations=concs,
            signals=signals,
            conc_unit=conc_unit,
            models=[standard.result],
            cutoff=cutoff,
        )

    def fit_models(self, silent: bool = False):
        """Fits all models to the given data.

        Args:
            silent (bool, optional): Silences the print output of
                the fitter. Defaults to False.
        """

        for model in self.models:
            # Set the calibration range of the model
            model.calibration_range = CalibrationRange(
                conc_lower=min(self.concentrations),
                conc_upper=max(self.concentrations),
                signal_lower=min(self.signals),
                signal_upper=max(self.signals),
            )

            y_data = np.array(self.signals)
            x_data = np.array(self.concentrations)

            # Fit model
            fitter = Fitter.from_calibration_model(model)
            statisctics = fitter.fit(
                y=y_data, x=x_data, indep_var_symbol=self.molecule_id
            )

            # Set the fit statistics
            model.statistics = statisctics
            model.was_fitted = True

        # Sort models by AIC
        self.models = sorted(self.models, key=lambda x: x.statistics.aic)

        if not silent:
            print("✅ Models have been fitted successfully.")
            self.print_result_table()

    def print_result_table(self) -> None:
        """
        Prints a table with the results of the fitted models.
        """

        console = Console()

        table = Table(title="Model Overview")
        table.add_column("Model Name", style="magenta")
        table.add_column("AIC", style="cyan")
        table.add_column("R squared", style="cyan")
        table.add_column("RMSD", style="cyan")
        table.add_column("Equation", style="cyan")
        table.add_column("Relative Parameter Standard Errors", style="cyan")

        for model in self.models:
            param_string = ""
            for param in model.parameters:
                if not param.stderr:
                    stderr = "n.a."
                else:
                    stderr = param.stderr / param.value
                    stderr = str(round(stderr * 100, 1)) + "%"
                param_string += f"{param.symbol}: {stderr}, "

            table.add_row(
                model.name,
                str(round(model.statistics.aic)),
                str(round(model.statistics.r2, 4)),
                str(round(model.statistics.rmsd, 4)),
                model.signal_law,
                param_string,
            )

        console.print(table)

    def visualize(self) -> None:
        """
        Visualizes the calibration curve and the residuals of the models.
        """
        fig = make_subplots(
            rows=1,
            cols=2,
            x_title=f"{self.molecule_name} / {self._format_unit(str(self.conc_unit))}",
            subplot_titles=[
                "Standard",
                "Model Residuals",
            ],
            horizontal_spacing=0.15,
        )
        colors = px.colors.qualitative.Plotly

        buttons = []
        if self.standard:
            fig = self._traces_from_standard(fig)
        else:
            fig.add_trace(
                go.Scatter(
                    x=self.concentrations,
                    y=self.signals,
                    name=f"{self.molecule_name}",
                    mode="markers",
                    marker=dict(color="#000000"),
                    visible=True,
                    customdata=[f"{self.molecule_name} standard"],
                ),
                col=1,
                row=1,
            )

        for model, color in zip(self.models, colors):
            fitter = Fitter.from_calibration_model(model)
            smooth_x = np.linspace(
                min(self.concentrations), max(self.concentrations), 100
            )

            params = {param.symbol: param.value for param in model.parameters}
            params[model.molecule_id] = smooth_x

            model_pred = fitter.lmfit_model.eval(**params)

            fitter.fit(self.signals, self.concentrations, model.molecule_id)
            residuals = fitter.lmfit_result.residual

            # Add model traces
            fig.add_trace(
                go.Scatter(
                    x=smooth_x,
                    y=model_pred,
                    name=f"{model.name} model",
                    mode="lines",
                    marker=dict(color=color),
                    visible=False,
                    customdata=[f"{model.name} model"],
                ),
                col=1,
                row=1,
            )

            # Add residual traces
            fig.add_trace(
                go.Scatter(
                    x=self.concentrations,
                    y=residuals,
                    name="Residuals",
                    mode="markers",
                    marker=dict(color=color),
                    hoverinfo="skip",
                    visible=False,
                    customdata=[f"{model.name} model"],
                ),
                col=2,
                row=1,
            )

            fig.add_trace(
                go.Scatter(
                    x=self.concentrations,
                    y=np.zeros(len(self.concentrations)),
                    line=dict(color="grey", width=2, dash="dash"),
                    visible=True,
                    customdata=[f"{model.name} model"],
                    showlegend=False,
                ),
                col=2,
                row=1,
            )

        buttons.append(
            dict(
                method="update",
                args=[
                    dict(
                        visible=self._visibility_mask(
                            visible_traces=[f"{self.molecule_name} standard"],
                            fig_data=fig.data,
                        )
                    )
                ],
                label=f"{self.molecule_name} standard",
            ),
        )

        for model in self.models:
            buttons.append(
                dict(
                    method="update",
                    args=[
                        dict(
                            visible=self._visibility_mask(
                                visible_traces=[
                                    f"{model.name} model",
                                    f"{self.molecule_name} standard",
                                ],
                                fig_data=fig.data,
                            ),
                            title=f"{model.name} model",
                        )
                    ],
                    label=f"{model.name} model",
                )
            )

        all_traces = [f"{model.name} model" for model in self.models]
        all_traces.append(f"{self.molecule_name} standard")
        buttons.append(
            dict(
                method="update",
                label="all",
                args=[
                    dict(
                        visible=self._visibility_mask(
                            visible_traces=all_traces,
                            fig_data=fig.data,
                        )
                    )
                ],
            )
        )

        fig.update_layout(
            updatemenus=[
                dict(
                    type="buttons",
                    direction="right",
                    active=0,
                    x=0,
                    y=1.2,
                    xanchor="left",
                    yanchor="top",
                    buttons=buttons,
                )
            ],
            margin=dict(l=20, r=20, t=100, b=60),
            template="simple_white",
        )

        if self.wavelength:
            signal_label = f"(E<sub>{self.wavelength:.0f} nm</sub>)"
        else:
            signal_label = "(a.u.)"

        fig.update_yaxes(
            title_text=f"{self.molecule_name} {signal_label}", row=1, col=1
        )
        fig.update_yaxes(
            title_text=f"Residuals {self.molecule_name} {signal_label}", row=1, col=2
        )
        fig.update_traces(hovertemplate="Signal: %{y:.2f}")

        config = {
            "toImageButtonOptions": {
                "format": "png",  # one of png, svg, jpeg, webp
                "filename": f"{self.molecule_name}_calibration_curve",
                # "height": 600,
                # "width": 700,
                "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
            }
        }

        return fig.show(config=config)

    def _traces_from_standard(self, fig: go.Figure):
        for sample in self.standard.samples:
            fig.add_trace(
                go.Scatter(
                    x=[sample.concentration],
                    y=[sample.signal],
                    name=sample.id,
                    mode="markers",
                    marker=dict(color="#000000"),
                    visible=True,
                    customdata=[f"{self.standard.name} standard"],
                    showlegend=False,
                ),
                col=1,
                row=1,
            )

        return fig

    def create_standard(
        self,
        model: CalibrationModel,
        ph: float,
        temperature: float,
        temp_unit: str = C,
        retention_time: Optional[float] = None,
    ) -> Standard:
        """Creates a standard object with the given model, pH, and temperature.

        Args:
            model (CalibrationModel): The fitted model to be used for the standard.
            ph (float): The pH value of the standard.
            temperature (float): The temperature of the standard.
            temp_unit (str): The unit of the temperature. Defaults to "C".

        Raises:
            ValueError: If the model has not been fitted yet.

        Returns:
            Standard: The created standard object.
        """

        if not model.was_fitted:
            raise ValueError("Model has not been fitted yet. Run 'fit_models' first.")

        standard = Standard(
            molecule_id=self.molecule_id,
            molecule_name=self.molecule_name,
            wavelength=self.wavelength,
            ph=ph,
            temp_unit=temp_unit,
            temperature=temperature,
            signal_type=None,
            samples=[],
            result=model,
            retention_time=retention_time,
        )

        for conc, signal in zip(self.concentrations, self.signals):
            standard.add_to_samples(
                concentration=conc, signal=signal, conc_unit=self.conc_unit
            )

        self.standard = standard

        return standard

    @staticmethod
    def _visibility_mask(visible_traces: list, fig_data: list) -> list:
        return [
            any(fig["customdata"][0] == trace for trace in visible_traces)
            for fig in fig_data
        ]

    @staticmethod
    def _format_unit(unit: str) -> str:
        unit = unit.replace("/l", " L<sup>-1</sup>")
        unit = unit.replace("1/s", "s<sup>-1</sup>")
        unit = unit.replace("1/min", "min<sup>-1</sup>")
        unit = unit.replace("umol", "µmol")
        unit = unit.replace("ug", "µg")
        return unit


if __name__ == "__main__":
    from calipytion.units import mM

    cal = Calibrator(
        molecule_id="s1",
        molecule_name="Nicotinamide adenine dinucleotide",
        conc_unit=mM,
        concentrations=[0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
        signals=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1],
    )

    print(cal)
