import sdRDM
import pandas as pd
import numpy as np

from plotly.subplots import make_subplots
from plotly import graph_objects as go
from typing import List, Optional, Any
from pydantic import Field
from sdRDM.base.listplus import ListPlus
from sdRDM.base.utils import forge_signature, IDGenerator

from astropy.units import UnitBase

from .parameter import Parameter
from .model import Model
from .standard import Standard
from ..ioutils.parsemodel import parse_model


@forge_signature
class Calibrator(sdRDM.DataModel):

    """"""

    id: Optional[str] = Field(
        description="Unique identifier of the given object.",
        default_factory=IDGenerator("calibratorINDEX"),
        xml="@id",
    )

    standard: Optional[Standard] = Field(
        default=Standard(),
        description="Standard data of a chemical species",
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

    models: List[Model] = Field(
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

    def __init__(self, **data: Any):
        super().__init__(**data)
        self._apply_cutoff()

    def add_to_models(
        self,
        name: Optional[str] = None,
        equation: Optional[str] = None,
        parameters: List[Parameter] = ListPlus(),
        aic: Optional[float] = None,
        bic: Optional[float] = None,
        r2: Optional[float] = None,
        residuals: List[float] = ListPlus(),
        rmsd: Optional[float] = None,
        id: Optional[str] = None,
    ) -> None:
        """
        This method adds an object of type 'Model' to attribute models

        Args:
            id (str): Unique identifier of the 'Model' object. Defaults to 'None'.
            name (): Name of the calibration model. Defaults to None
            equation (): Equation of the calibration model. Defaults to None
            parameters (): Parameters of the calibration model equation. Defaults to ListPlus()
            aic (): Akaike information criterion. Defaults to None
            bic (): Bayesian information criterion. Defaults to None
            r2 (): Coefficient of determination. Defaults to None
            residuals (): Residuals of the calibration model. Defaults to ListPlus()
            rmsd (): Root mean square deviation. Defaults to None
        """

        params = {
            "name": name,
            "equation": equation,
            "parameters": parameters,
            "aic": aic,
            "bic": bic,
            "r2": r2,
            "residuals": residuals,
            "rmsd": rmsd,
        }

        if id is not None:
            params["id"] = id

        self.models.append(Model(**params))

        return self.models[-1]

    def _apply_cutoff(self):

        if self.cutoff:
            below_cutoff_idx = [idx for idx,
                                signal in enumerate(self.signals) if signal < self.cutoff]

            self.concentrations = [self.concentrations[idx]
                                   for idx in below_cutoff_idx]
            self.signals = [self.signals[idx] for idx in below_cutoff_idx]

    @classmethod
    def from_standard(
        cls,
        standard: Standard,
        cutoff: float = None,
        models: List[Model] = ListPlus(),
    ):

        # get concentrations and corresponding signals as lists
        concentrations = [sample.concentration for sample in standard.samples]
        signals = [sample.signal for sample in standard.samples]
        if not len(concentrations) == len(signals):
            raise ValueError(
                "Number of concentrations and signals must be the same"
            )

        # verify that all samples have the same concentration unit
        if not all([sample.conc_unit == standard.samples[0].conc_unit for sample in standard.samples]):
            raise ValueError(
                "All samples must have the same concentration unit")
        conc_unit = standard.samples[0].conc_unit

        return cls(
            standard=standard,
            concentrations=concentrations,
            conc_unit=conc_unit,
            signals=signals,
            cutoff=cutoff,
            models=models,
        )

    def fit_models(self, init_param_value: float = 0.1):

        for model in self.models:
            model.fit(self.concentrations, self.signals,
                      init_param_value=init_param_value)

        return self.fit_statistics

    def _get_models_overview(self) -> pd.DataFrame:
        """
        Returns a dataframe with an overview of the
        fit statistics (AIC, R squared, RMSD) for each model.
        """

        # check if models have been fitted
        if not all([model.aic for model in self.models]):
            raise ValueError(
                "Models have not been fitted yet. Run 'fit_models' first.")

        # get model statistics
        model_stats = []
        for model in self.models:
            model_stats.append(
                {
                    "Model Name": model.name,
                    "AIC": round(model.aic),
                    "R squared": round(model.r2, 4),
                    "RMSD": round(model.rmsd, 4),
                }
            )

        # create and format dataframe
        df = pd.DataFrame(model_stats).set_index(
            "Model Name").sort_values("AIC")

        decimal_formatting = {
            'RMSD': '{:.4f}',
            'R squared': '{:.4f}',
            'AIC': '{:.0f}'
        }

        return df.style.format(decimal_formatting).background_gradient(cmap="Blues")

    @property
    def fit_statistics(self):
        return self._get_models_overview()

    def visualize(self, model: Model):

        fig = make_subplots(
            rows=1,
            cols=2,
            x_title=f"{self.standard.name} concentration ({self.conc_unit})",
            subplot_titles=[
                "Standard",
                "Model Residuals",
            ],
            horizontal_spacing=0.15,
        )

        fig.add_trace(
            go.Scatter(
                x=self.concentrations,
                y=self.signals,
                name=f"{self.standard.name}",
                mode="markers",
                marker=dict(color="#1f77b4"),
                hoverinfo="skip",
                visible=True,
            ),
            col=1,
            row=1,
        )

        smooth_x = np.linspace(
            self.concentrations[0],
            self.concentrations[-1],
            len(self.concentrations) * 5,
        )

        model_callable, _ = model._get_model_callable(
            solve_for="signal", dependent_variable="concentration"
        )

        model_data = model_callable(
            np.array(self.concentrations), **model._params)
        smooth_model_data = model_callable(smooth_x, **model._params)
        percentual_residuals = np.divide(
            model.residuals,
            model_data,
            out=np.zeros_like(model.residuals),
            where=model_data != 0,
        ) * 100

        fig.add_trace(
            go.Scatter(
                x=smooth_x,
                y=smooth_model_data,
                name=f"{model.name} model",
                mode="lines",
                marker=dict(color="#1f77b4"),
                # marker=dict(color=self._HEX_to_RGBA_string(color)),
                # showlegend=show_legend,
                # customdata=["replicates"],
                hoverinfo="skip",
                visible=True,
            ),
            col=1,
            row=1,
        )
        fig.add_trace(
            go.Scatter(
                x=self.concentrations,
                y=percentual_residuals,
                name="Residuals",
                mode="markers",
                marker=dict(color="#d62728"),
                hoverinfo="skip",
                visible=True,
            ),
            col=2,
            row=1,
        )
        fig.add_hline(
            y=0, line_dash="dot", row=1, col=2, line_color="#000000", line_width=2
        )

        fig.update_yaxes(title_text="Signal (a.u.)", row=1, col=1)
        fig.update_yaxes(title_text="Residuals (%)", row=1, col=2)

        config = {
            "toImageButtonOptions": {
                "format": "svg",  # one of png, svg, jpeg, webp
                "filename": f"{model.name}_calibration_curve",
                # "height": 600,
                # "width": 700,
                "scale": 1,  # Multiply title/legend/axis/canvas sizes by this factor
            }
        }

        return fig.show(config=config)

    def save_fitted_model(self, model: Model) -> Standard:

        if not model.aic:
            raise ValueError(
                "Model has not been fitted yet. Run 'fit_models' first.")

        self.standard.model_result = model

        return self.standard
