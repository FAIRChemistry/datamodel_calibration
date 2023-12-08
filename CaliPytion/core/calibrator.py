import sdRDM

import pandas as pd
import numpy as np
import plotly.express as px
from typing import Any, List, Optional
from pydantic import PrivateAttr, Field, validator
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator
from astropy.units import UnitBase
from plotly.subplots import make_subplots
from plotly import graph_objects as go
from IPython.display import display
from .standard import Standard
from .fitstatistics import FitStatistics
from .calibrationrange import CalibrationRange
from .parameter import Parameter
from .calibrationmodel import CalibrationModel


@forge_signature
class Calibrator(sdRDM.DataModel):
    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibratorINDEX"),
        xml="@id",
    )

    standard: Optional[Standard] = Field(
        description="Standard data of a chemical species",
        default_factory=Standard,
    )

    concentrations: List[float] = Field(
        description="Concentrations of the species",
        default_factory=ListPlus,
        multiple=True,
    )

    conc_unit: Optional[UnitBase] = Field(
        default=None,
        description="Concentration unit",
    )

    signals: List[float] = Field(
        description="Measured signals, corresponding to the concentrations",
        default_factory=ListPlus,
        multiple=True,
    )

    models: List[CalibrationModel] = Field(
        description="Potential models, describing the standard data",
        default_factory=ListPlus,
        multiple=True,
    )

    cutoff: Optional[float] = Field(
        default=None,
        description=(
            "Upper cutoff value for the measured signal. All signals above this value"
            " will be ignored during calibration"
        ),
    )
    __repo__: Optional[str] = PrivateAttr(
        default="https://github.com/FAIRChemistry/CaliPytion"
    )
    __commit__: Optional[str] = PrivateAttr(
        default="c48581a9bd1b6ecd079cb059c295f67f1f905502"
    )

    def add_to_models(
        self,
        name: Optional[str] = None,
        equation: Optional[str] = None,
        parameters: List[Parameter] = ListPlus(),
        was_fitted: Optional[bool] = None,
        calibration_range: Optional[CalibrationRange] = None,
        statistics: Optional[FitStatistics] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'CalibrationModel' to attribute models

        Args:
            id (str): Unique identifier of the 'CalibrationModel' object. Defaults to 'None'.
            name (): Name of the calibration model. Defaults to None
            equation (): Equation of the calibration model. Defaults to None
            parameters (): Parameters of the calibration model equation. Defaults to ListPlus()
            was_fitted (): Indicates if the model was fitted to the data. Defaults to None
            calibration_range (): Concentration and signal bounds in which the calibration model is valid.. Defaults to None
            statistics (): Fit statistics of the calibration model. Defaults to None
        """
        params = {
            "name": name,
            "equation": equation,
            "parameters": parameters,
            "was_fitted": was_fitted,
            "calibration_range": calibration_range,
            "statistics": statistics,
        }
        if id is not None:
            params["id"] = id
        self.models.append(CalibrationModel(**params))
        return self.models[-1]

    @validator("models", pre=True, always=True)
    def initialize_models(cls, models):
        # If models are not provided during initialization, import from tools.equations.py
        if not models:
            from CaliPytion.tools.equations import linear, quadratic, cubic

            models = [linear, quadratic, cubic]

            return models

    def __init__(self, **data: Any):
        super().__init__(**data)
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
            standard=standard,
            concentrations=concentrations,
            conc_unit=conc_unit,
            signals=signals,
            cutoff=cutoff,
            **kwargs,
        )

    def fit_models(
        self, init_param_value: float = 0.1, display_statistics: bool = True
    ):
        models = []
        for model in self.models:
            models.append(
                model.fit(
                    self.concentrations, self.signals, init_param_value=init_param_value
                )
            )
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
