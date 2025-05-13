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


class BiplotVisualizer(BasePlotter):
    """Exact match to original biplot functionality."""

    def create_biplot(self, pca_model, x_standardized, df, feature_to_group=None,
                      feature_groups_colors=None, text_dist=1.1, top_n=10,
                      enable_feature_grouping=False, significance_threshold=0.2, focus_on_loadings=False):
        """
        Create a biplot visualization with optional feature grouping and significance-based filtering.
        """
        if not hasattr(pca_model, 'components_'):
            raise ValueError("Please run PCA analysis first.")

        if self.fig is None or self.ax is None:  # Reinitialize if missing
            self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100)
        else:
            self.ax.clear()  # Clear the existing axes for re-plotting

        # Top N features based on loading magnitude
        loadings = pca_model.components_.T
        feature_names = df.columns
        loading_magnitudes = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_indices = np.argsort(loading_magnitudes)[::-1][:top_n]

        # Variance-based scaling
        variance_scale = np.sqrt(pca_model.explained_variance_[:2])
        scaled_loadings = loadings[:, :2] * variance_scale

        # Clear the plot
        self.clear_plot()

        # Configure plot appearance
        self.ax.grid(True, linestyle='--', alpha=0.3)
        self.ax.set_facecolor('#f8f9fa')

        # Scatter plot for samples
        scores = pca_model.transform(x_standardized)
        self.ax.scatter(scores[:, 0], scores[:, 1], alpha=0.2, color='gray', s=30, label='Samples')

        # Confidence ellipse
        confidence_ellipse = stats.chi2.ppf(0.95, df=2)
        eigenvals = pca_model.explained_variance_[:2]
        ellipse = Ellipse(
            (0, 0),
            width=2 * np.sqrt(eigenvals[0] * confidence_ellipse),
            height=2 * np.sqrt(eigenvals[1] * confidence_ellipse),
            alpha=0.1, color='gray', linestyle='--'
        )
        self.ax.add_patch(ellipse)

        # Text annotations
        texts = []

        # Calculate axis limits dynamically based on PCA scores and loadings
        if focus_on_loadings:
            x_min, x_max = np.min(scaled_loadings[top_indices, 0]), np.max(scaled_loadings[top_indices, 0])
            y_min, y_max = np.min(scaled_loadings[top_indices, 1]), np.max(scaled_loadings[top_indices, 1])
        else:
            x_min, x_max = np.min(scores[:, 0]), np.max(scores[:, 0])
            y_min, y_max = np.min(scores[:, 1]), np.max(scores[:, 1])

        # Add a margin to avoid cutting off arrows or points
        margin = 0.2 * max(x_max - x_min, y_max - y_min)  # 20% margin of the larger range
        self.ax.set_xlim(x_min - margin, x_max + margin)
        self.ax.set_ylim(y_min - margin, y_max + margin)

        if enable_feature_grouping and feature_to_group:
            # Dynamically generate color palette for unique groups
            unique_groups = set(feature_to_group.values())
            colormap = cm.get_cmap('tab10', len(unique_groups))
            group_colors = {group: to_hex(colormap(i)) for i, group in enumerate(sorted(unique_groups))}
            for idx in top_indices:
                feature = feature_names[idx].lower()
                magnitude = loading_magnitudes[idx]

                # Skip features below the significance threshold
                if magnitude < significance_threshold:
                    continue

                # Get the group for the feature
                group = feature_to_group.get(feature, "Unknown")
                color = feature_groups_colors.get(group, "gray")

                # Plot the arrow
                arrow = FancyArrowPatch(
                    (0, 0),
                    (scaled_loadings[idx, 0], scaled_loadings[idx, 1]),
                    color=color,
                    arrowstyle='->',
                    mutation_scale=15,
                    alpha=0.8
                )
                self.ax.add_patch(arrow)
                
                # Add the feature label
                text = self.ax.text(
                    scaled_loadings[idx, 0] * text_dist,
                    scaled_loadings[idx, 1] * text_dist,
                    feature, fontsize=10, color=color,
                    ha='center', va='center'
                )
                texts.append(text)

            # Add legend for groups
            for group, color in feature_groups_colors.items():
                self.ax.plot([], [], '-', color=color, label=group, linewidth=2)
            self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # No feature mapping provided
        else:
            # Generate dynamic colors for features
            colormap = cm.get_cmap('tab20', len(top_indices))  # Dynamic color palette based on Top N
            colors = [to_hex(colormap(i)) for i in range(len(top_indices))]

            for idx, color in zip(top_indices, colors):
                feature = feature_names[idx].lower()
                magnitude = loading_magnitudes[idx]

                # Skip features below the significance threshold
                if magnitude < significance_threshold:
                    continue

                # Add arrow and label
                arrow = FancyArrowPatch(
                    (0, 0),
                    (scaled_loadings[idx, 0], scaled_loadings[idx, 1]),
                    color=color,
                    arrowstyle='->',
                    mutation_scale=15,
                    alpha=0.8
                )
                self.ax.add_patch(arrow)
                text = self.ax.text(
                    scaled_loadings[idx, 0] * text_dist,
                    scaled_loadings[idx, 1] * text_dist,
                    feature, fontsize=10, color=color,
                    ha='center', va='center'
                )
                texts.append(text)

            # Optional legend for features
            for idx, color in zip(top_indices, colors):
                self.ax.plot([], [], '-', color=color, label=feature_names[idx], linewidth=2)
            self.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        adjust_text(
            texts,
            arrowprops=dict(
                arrowstyle='->',
                color='gray',
                alpha=0.5,
                lw=0.5,
                shrinkA=5,  # Moves arrowhead away from text
                shrinkB=5  # Moves arrow tail away from origin
            ),
            force_text=1.5,  # Increased repulsion force to avoid overlaps
            force_points=0.8,  # Avoid overlapping with points
            expand_text=(1.5, 1.5),  # More spacing between labels
            expand_points=(1.2, 1.2),  # Ensure spacing from points
            lim=500  # Higher limit for iterations if overlaps persist
        )

        # Dynamically adjust axes limits and margins
        if focus_on_loadings:
            x_min, x_max = np.min(scaled_loadings[top_indices, 0]), np.max(scaled_loadings[top_indices, 0])
            y_min, y_max = np.min(scaled_loadings[top_indices, 1]), np.max(scaled_loadings[top_indices, 1])
        else:
            x_min, x_max = np.min(scores[:, 0]), np.max(scores[:, 0])
            y_min, y_max = np.min(scores[:, 1]), np.max(scores[:, 1])

        # Add a larger margin to reduce crowding
        margin = 0.25 * max(x_max - x_min, y_max - y_min)  # 25% margin
        self.ax.set_xlim(x_min - margin, x_max + margin)
        self.ax.set_ylim(y_min - margin, y_max + margin)

        # Set axis labels with explained variance
        var_explained = pca_model.explained_variance_ratio_
        self.ax.set_xlabel(f"PC1 ({var_explained[0]:.1%} explained var.)")
        self.ax.set_ylabel(f"PC2 ({var_explained[1]:.1%} explained var.)")
        self.ax.set_title(f"Biplot with Top {top_n} Significant Features")

        # Equal aspect ratio for clarity
        self.ax.set_aspect('equal', adjustable='box')


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


class BiplotManager:
    """
    Manages feature-to-group mappings for PCA biplots.
    """

    def __init__(self):
        self.feature_to_group = {}  # Mapping of features to groups
        self.group_colors = {}  # Colors for groups


    def load_group_mapping(self, df):
        """
        Load feature-to-group mapping from a DataFrame.

        :param df: DataFrame with columns 'Feature' and 'Group'.
        """
        # Validate input DataFrame
        if 'Feature' not in df.columns or 'Group' not in df.columns:
            raise ValueError("Mapping CSV must contain 'Feature' and 'Group' columns.")

        # Create feature-to-group mapping and standardize to lowercase
        self.feature_to_group = {key.lower(): value for key, value in zip(df['Feature'], df['Group'])}

        # Get unique groups
        unique_groups = sorted(df['Group'].unique())

        # Generate a dynamic color palette for groups
        colormap = cm.get_cmap('tab10', len(unique_groups))  # Use a colormap with sufficient distinct colors
        self.group_colors = {
            group: to_hex(colormap(i)) for i, group in enumerate(unique_groups)
        }



    def get_group(self, feature):
        """
        Get the group of a given feature.

        :param feature: Feature name.
        :return: Group name.
        """
        return self.feature_to_group.get(feature, "Unknown")

    def get_color(self, group):
        """
        Get the color assigned to a given group.

        :param group: Group name.
        :return: Color.
        """
        return self.group_colors.get(group, 'gray')