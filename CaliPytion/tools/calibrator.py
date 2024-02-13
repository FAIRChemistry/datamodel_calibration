from os import name
import sdRDM

import pandas as pd
from pydantic import BaseModel
import numpy as np
import plotly.express as px
from typing import Any, List, Optional
from pydantic import PrivateAttr, Field, validator
from plotly.subplots import make_subplots
from plotly import graph_objects as go
from IPython.display import display
from ..core.parameter import Parameter
from ..core.fitstatistics import FitStatistics
from ..core.calibrationrange import CalibrationRange
from ..core.calibrationmodel import CalibrationModel
from ..core.standard import Standard


class Calibrator(BaseModel):


    species_id: str = Field(
        description="Unique identifier of the given object.",
    )

    name: Optional[str] = Field(
        description="Name of the standard",
    )

    concentrations: List[float] = Field(
        description="Concentrations of the standard",
        multiple=True,
    )

    conc_unit: str = Field(
        description="Concentration unit",
    )

    signals: List[float] = Field(
        description="Measured signals, corresponding to the concentrations",
        multiple=True,
    )

    models: List[CalibrationModel] = Field(
        description="Potential models, which are used for fitting",
        multiple=True,
        default=None,
    )

    cutoff: Optional[float] = Field(
        default=None,
        description=(
            "Upper cutoff value for the measured signal. All signals above this value"
            " will be ignored during calibration"
        ),
    )

    def add_model(
        self,
        name: Optional[str] = None,
        equation: Optional[str] = None,
    ) -> None:
        
        model = CalibrationModel(
            name=name,
            equation=equation,
        )

        model = model._replace_equction_id(self.species_id)

        model._create_parameters(self.species_id)

        self.models.append(model)



    @validator("models", pre=True, always=True)
    def initialize_models(cls, models, values):

        if not models:
            species_id = values.get("species_id")
            from CaliPytion.tools.equations import linear, quadratic, cubic

            for model in [linear, quadratic, cubic]:
                model.signal_equation.replace("signal", f"{species_id}")

            models = [linear, quadratic, cubic]

            return models

    def __init__(self, **data):
        super().__init__(**data)
        for model in self.models:
            model._replace_equction_id(self.species_id)
            model._create_parameters(self.species_id)
        self._apply_cutoff() 

    def _apply_cutoff(self):
        if self.cutoff:
            below_cutoff_idx = [
                idx for idx, signal in enumerate(self.signals) if signal < self.cutoff
            ]

            self.concentrations = [self.concentrations[idx] for idx in below_cutoff_idx]
            self.signals = [self.signals[idx] for idx in below_cutoff_idx]

    def get_model(self, model_name: str) -> CalibrationModel:
        """
        This method returns a model by its name

        Args:
            model_name (str): Name of the model to be returned

        Returns:
            CalibrationModel: Object of type 'CalibrationModel'
        """

        for model in self.models:
            if model.name == model_name:
                return model

        raise ValueError(f"Model '{model_name}' not found")

    @classmethod
    def from_standard(
        cls,
        standard: Standard,
        cutoff: float = None,
        **kwargs,
    ):
        # get concentrations and corresponding signals as lists
        concentrations = [sample.concentration for sample in standard.samples]
        signals = [sample.signal for sample in standard.samples]
        if not len(concentrations) == len(signals):
            raise ValueError("Number of concentrations and signals must be the same")

        # verify that all samples have the same concentration unit
        if not all([
            sample.conc_unit == standard.samples[0].conc_unit
            for sample in standard.samples
        ]):
            raise ValueError("All samples must have the same concentration unit")
        conc_unit = standard.samples[0].conc_unit

        return cls(
            species_id=standard.species_id,
            name=standard.name,
            standard=standard,
            concentrations=concentrations,
            conc_unit=conc_unit,
            signals=signals,
            cutoff=cutoff,
            **kwargs,
        )

    def fit_models(
        self, display_statistics: bool = True
    ):
        models = []
        for model in self.models:
            models.append(
                model.fit(
                    concentrations=self.concentrations, signals=self.signals
                )
            )

        self.models.sort(key=lambda x: x.statistics.aic)

        if display_statistics:
            display(self.fit_statistics)

    def _get_models_overview(self) -> pd.DataFrame:
        """
        Returns a dataframe with an overview of the
        fit statistics (AIC, R squared, RMSD) for each model.
        """

        # check if models have been fitted
        if not all([model.was_fitted for model in self.models]):
            raise ValueError("Models have not been fitted yet. Run 'fit_models' first.")

        # get model statistics
        model_stats = []
        for model in self.models:
            if model.was_fitted:
                model_stats.append({
                    "Model Name": model.name,
                    "AIC": round(model.statistics.aic),
                    "R squared": round(model.statistics.r2, 4),
                    "RMSD": round(model.statistics.rmsd, 4),
                })
            else:
                model_stats.append({
                    "Model Name": model.name,
                    "AIC": "-",
                    "R squared": "-",
                    "RMSD": "-",
                })

        # create and format dataframe
        df = pd.DataFrame(model_stats).set_index("Model Name").sort_values("AIC")

        decimal_formatting = {"RMSD": "{:.4f}", "R squared": "{:.4f}", "AIC": "{:.0f}"}

        return (
            df.style.format(decimal_formatting, na_rep="")
            .background_gradient(cmap="Blues")
            .background_gradient(cmap="Blues", subset=["AIC"], gmap=-df["AIC"])
            .background_gradient(cmap="Blues", subset=["RMSD"], gmap=-df["RMSD"])
        )

    @property
    def fit_statistics(self):
        return self._get_models_overview()

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

    def visualize(self):
        fig = make_subplots(
            rows=1,
            cols=2,
            x_title=f"{self.standard.name} / {self._format_unit(str(self.conc_unit))}",
            subplot_titles=[
                "Standard",
                "Model Residuals",
            ],
            horizontal_spacing=0.15,
        )
        colors = px.colors.qualitative.Plotly

        buttons = []
        if self.standard.samples:
            fig = self._traces_from_standard(fig)
        else:
            fig.add_trace(
                go.Scatter(
                    x=self.concentrations,
                    y=self.signals,
                    name=f"{self.standard.name} standard",
                    mode="markers",
                    marker=dict(color="#000000"),
                    visible=True,
                    customdata=[f"{self.standard.name} standard"],
                ),
                col=1,
                row=1,
            )

        smooth_x = np.linspace(
            min(self.concentrations),
            max(self.concentrations),
            len(self.concentrations) * 5,
        )
        for model, color in zip(self.models, colors):
            model_data = model.signal_callable(self.concentrations, **model._params)
            model_residuals = model._get_residuals(self.concentrations, self.signals)

            smooth_model_data = model.signal_callable(smooth_x, **model._params)

            # Add model traces
            fig.add_trace(
                go.Scatter(
                    x=smooth_x,
                    y=smooth_model_data,
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
                    y=model_residuals,
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
                            visible_traces=[f"{self.standard.name} standard"],
                            fig_data=fig.data,
                        )
                    )
                ],
                label=f"{self.standard.name} standard",
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
                                    f"{self.standard.name} standard",
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
        all_traces.append(f"{self.standard.name} standard")
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

        if self.standard:
            fig.update_yaxes(
                title_text=f"E<sub>{self.standard.wavelength:.0f} nm <sub>",
                row=1,
                col=1,
            )
            fig.update_yaxes(
                title_text=f"Residuals E<sub>{self.standard.wavelength:.0f} nm <sub>",
                row=1,
                col=2,
            )

        else:
            fig.update_yaxes(title_text="Signal (a.u.)", row=1, col=1)
            fig.update_yaxes(title_text="Residuals signal (a.u.)", row=1, col=1)
        fig.update_traces(hovertemplate="Signal: %{y:.2f}")

        config = {
            "toImageButtonOptions": {
                "format": "svg",  # one of png, svg, jpeg, webp
                "filename": f"{self.standard.name}_calibration_curve",
                # "height": 600,
                # "width": 700,
                "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
            }
        }

        return fig.show(config=config)

    def save_model(self, model: CalibrationModel) -> Standard:
        if isinstance(model, str):
            model = self.get_model(model)

        if not model.was_fitted:
            raise ValueError("Model has not been fitted yet. Run 'fit_models' first.")

        self.standard.model_result = model

        return self.standard

    @staticmethod
    def _visibility_mask(visible_traces: list, fig_data: list) -> list:
        return [
            any(fig["customdata"][0] == trace for trace in visible_traces)
            for fig in fig_data
        ]

    @staticmethod
    def _format_unit(unit: str) -> str:
        unit = unit.replace(" / l", " L<sup>-1</sup>")
        unit = unit.replace("1 / s", "s<sup>-1</sup>")
        unit = unit.replace("1 / min", "min<sup>-1</sup>")
        unit = unit.replace("umol", "µmol")
        unit = unit.replace("ug", "µg")
        return unit
