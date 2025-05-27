import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import to_hex
from matplotlib.colors import Normalize
from matplotlib.patches import Ellipse, FancyArrowPatch
from scipy import stats
import plotly.graph_objects as go
import plotly.io as pio
from adjustText import adjust_text
import os
import time
from .base import BasePlotter
from ..utils.helpers import generate_color_palette


def generate_significance_color(magnitude, min_magnitude, max_magnitude):
    """Preserve original color generation for significance."""
    normalized = (magnitude - min_magnitude) / (max_magnitude - min_magnitude)
    colormap = cm.viridis
    return colormap(normalized)



class InteractiveBiplotVisualizer:
    """Exact match to original interactive biplot functionality."""

    def create_interactive_biplot(self, pca_model, x_standardized, data,
                                  top_n_entry, text_distance_entry,
                                  enable_feature_grouping, feature_to_group,
                                  significance_threshold=0.2):
        """Create interactive biplot matching original exactly."""
        if pca_model is None:
            raise ValueError("Please run PCA analysis first.")

        # Get top N features - exact match
        try:
            top_n = int(top_n_entry.get())
        except ValueError:
            top_n = 10

        loadings = pca_model.components_.T
        feature_names = data.columns
        text_distance = float(text_distance_entry.get())

        # Calculate loadings - matching original
        loading_magnitudes = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_indices = np.argsort(loading_magnitudes)[::-1][:top_n]
        variance_scale = np.sqrt(pca_model.explained_variance_[:2])
        scaled_loadings = loadings[:, :2] * variance_scale

        fig = go.Figure()

        # Add samples - exact match
        scores = pca_model.transform(x_standardized)
        fig.add_trace(go.Scatter(
            x=scores[:, 0], y=scores[:, 1],
            mode='markers',
            marker=dict(color='lightgray', size=6, opacity=0.3),
            name='Samples',
            hoverinfo='skip',
            visible=True
        ))

        # Feature grouping color scheme - matching original
        if enable_feature_grouping and feature_to_group:
            group_colors = {
                "FAB": "#1f77b4",
                "non-FAB": "#ff7f0e",
                "RAA": "#d62728",
                "Beneficials": "#2ca02c",
                "non-RAA pests": "#9467bd"
            }

            # Add grouped features - exact match
            legend_groups = set()
            for idx in top_indices:
                feature = feature_names[idx]
                magnitude = loading_magnitudes[idx]
                if magnitude > significance_threshold:
                    group = feature_to_group.get(feature, "Unknown")
                    color = group_colors.get(group, "gray")

                    showlegend = group not in legend_groups
                    legend_groups.add(group)

                    fig.add_trace(go.Scatter(
                        x=[0, scaled_loadings[idx, 0]],
                        y=[0, scaled_loadings[idx, 1]],
                        mode="lines+markers",
                        line=dict(color=color, width=2),
                        marker=dict(color=color),
                        name=group if showlegend else feature,
                        legendgroup=group,
                        showlegend=showlegend,
                        hovertext=(f"Feature: {feature}<br>"
                                   f"Group: {group}<br>"
                                   f"Loading PC1: {scaled_loadings[idx, 0]:.3f}<br>"
                                   f"Loading PC2: {scaled_loadings[idx, 1]:.3f}<br>"
                                   f"Magnitude: {magnitude:.3f}"),
                        hoverinfo="text"
                    ))
        else:
            # Un-grouped features - matching original
            colors = [
                '#4B0082', '#0000FF', '#00FF00',
                '#FFFF00', '#FF7F00', '#FF0000'
            ]

            for idx in top_indices:
                magnitude = loading_magnitudes[idx]
                if magnitude > significance_threshold:
                    color_idx = int((len(colors) - 1) * magnitude / max(loading_magnitudes))
                    color_idx = min(color_idx, len(colors) - 1)
                    color = colors[color_idx]

                    fig.add_trace(go.Scatter(
                        x=[0, scaled_loadings[idx, 0]],
                        y=[0, scaled_loadings[idx, 1]],
                        mode="lines+markers",
                        line=dict(color=color, width=2),
                        marker=dict(color=color),
                        name=feature_names[idx],
                        hovertext=(f"Feature: {feature_names[idx]}<br>"
                                   f"Loading PC1: {scaled_loadings[idx, 0]:.3f}<br>"
                                   f"Loading PC2: {scaled_loadings[idx, 1]:.3f}<br>"
                                   f"Magnitude: {magnitude:.3f}"),
                        hoverinfo="text"
                    ))

        # Add interactivity - exact match to original
        fig.update_layout(
            updatemenus=[{
                "type": "buttons",
                "buttons": [
                    dict(label="Show All Features",
                         method="update",
                         args=[{"visible": [True] * len(fig.data)}]),
                    dict(label="Show Top 10",
                         method="update",
                         args=[{"visible": [i < 10 for i in range(len(fig.data))]}]),
                ],
                "direction": "down",
                "showactive": True,
                "x": 0.1,
                "y": 1.1,
                "xanchor": "left",
                "yanchor": "top"
            }],
            sliders=[{
                "steps": [
                    dict(
                        method="update",
                        args=[{"visible": [abs(loading_magnitudes[i]) > t for i in range(len(top_indices))]}],
                        label=f"{t:.1f}"
                    ) for t in np.linspace(0, 1, 10)
                ],
                "currentvalue": {"prefix": "Significance Threshold: "}
            }]
        )

        # Update layout - matching original
        var_explained = pca_model.explained_variance_ratio_
        fig.update_layout(
            title=f"Interactive Biplot with Top {top_n} Significant Features",
            xaxis_title=f"PC1 ({var_explained[0]:.1%} explained var.)",
            yaxis_title=f"PC2 ({var_explained[1]:.1%} explained var.)",
            clickmode='event+select',
            showlegend=True,
            legend=dict(
                title="Feature Groups" if enable_feature_grouping else "Features",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )

        return fig

    def save_interactive_biplot(self, fig, output_dir):
        """Save interactive biplot matching original exactly."""
        current_time = time.strftime("%Y%m%d-%H%M%S")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        save_path = os.path.join(output_dir, f"Interactive_Biplot_{current_time}.html")
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'editable': True
        }
        pio.write_html(fig, file=save_path, config=config)
        return save_path



    