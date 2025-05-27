import os
import time
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
from matplotlib import cm, pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.patches import Ellipse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io


from scipy import stats

from source.gui.app_state  import AppState

from adjustText import adjust_text


from source.utils.constant import *

import source.utils.file_operations as file_ops


class BiplotBox(tk.Frame):
    """
    Creats a space for Biplot generation buttons
    """

    def __init__(self, main, app_state: AppState, **kwargs):
        super().__init__(main, **kwargs)

        self.app_state = app_state

        # Variables
        self.enable_feature_grouping = tk.BooleanVar(value=False)

        # Biplot Banner
        self.biplot_banner = None

        # Feature Grouping
        self.grouping_checkbox = None
        self.mapping_label = None
        self.mapping_button = None

        # Analysis Buttons
        self.biplot_button = None
        self.interactive_biplot_button = None
        self.scree_plot_button = None
        self.top_features_button = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        # Banner
        self.biplot_banner = tk.Label(self, **BANNER_STYLE, text="Biplot Section")
        
        # Feature Grouping Section
        self.grouping_checkbox = tk.Checkbutton(self, text="Enable Feature Grouping",
                                                variable=self.enable_feature_grouping,
                                                **LABEL_STYLE,
                                                command=self.toggle_feature_grouping
        )
        self.mapping_label = tk.Label(self, **LABEL_STYLE,
                                      text="Feature-to-Group Mapping (Optional):")
        self.mapping_button = tk.Button(self, text="Upload Mapping CSV", **BUTTON_STYLE,
                                        command=self.upload_mapping_csv)
        self.mapping_button.config(state="normal")

        # Analysis Buttons
        self.biplot_button = tk.Button(self, text="Biplot with Groups", **BUTTON_STYLE,
                                       command=self.create_biplot)
        self.interactive_biplot_button = tk.Button(self, text="Interactive Biplot", **BUTTON_STYLE,
                                                   command=self.create_interactive_biplot)
        self.scree_plot_button = tk.Button(self, text="Show Scree Plot", **BUTTON_STYLE,
                                           command=self.create_scree_plot)
        self.top_features_button = tk.Button(self, text="Top Features Loadings", **BUTTON_STYLE,
                                             command=self.plot_top_features_loadings)

    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Banners
        self.biplot_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Feature Grouping
        self.grouping_checkbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.mapping_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.mapping_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Visualization Buttons
        self.scree_plot_button.grid(row=3, column=0, padx=5, pady=5)
        self.biplot_button.grid(row=3, column=1, padx=5, pady=5)
        self.interactive_biplot_button.grid(row=4, column=0, padx=5, pady=5)
        self.top_features_button.grid(row=4, column=1, padx=5, pady=5)


    #### 2. VISUALIZATION METHODS ####

    def create_scree_plot(self):
        """Create scree plot."""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return
        
        try:
            # Get the explained variance
            __, __, explained_variance, __, __ = self.get_pca_data()
            
            self.init_scree_fig()

            # Bar plot of individual explained variance
            self.app_state.ax.bar(
                range(1, len(explained_variance) + 1),
                explained_variance,
                alpha=0.7,
                align='center'
            )

            # Step plot of cumulative explained variance
            self.app_state.ax.step(
                range(1, len(explained_variance) + 1),
                np.cumsum(explained_variance),
                where='mid',
                label='Cumulative explained variance'
            )

            # Updates the figure on the GUI
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating scree plot: {str(e)}")

    def create_biplot(self):
        """Create biplot visualization."""
        # Validates Input Data
        if not self.validate_biplot_data(): return

        # Runs PCA analysis and gets relavent values
        scores, loadings, variance, eigenvals, feat_names = self.get_pca_data()

        # Calculates other need information based on the PCA Resulats
        top_idx, loading_magnitudes, num_feat = self.get_top_pca_features(loadings)
        top_feat = self.app_state.df.columns[top_idx]

        try:
            if not self.init_biplot_fig(variance, num_feat): return 
            
            # Calculate axis limits with margin
            scaled_loadings = self.scale_loadings(eigenvals, loadings)
            self.set_biplot_axis_limits(scaled_loadings, top_idx)

            # Scatter plot for samples
            self.app_state.ax.scatter(scores[:, 0], scores[:, 1], alpha=0.2, color='gray', s=30, label='Samples')

            # Creates an elipse to represent confidence
            ellipse = self.create_confidence_elipse(eigenvals)
            
            # Adds elipse to the figure
            self.app_state.ax.add_patch(ellipse)

            # Creates biplot arrows and text for arrows and adds them to the plot
            self.add_biplot_arrows(top_feat, top_idx, feat_names, loading_magnitudes, scaled_loadings)
            
            # Add legend for groups
            for group, color in self.app_state.feat_colors.items():
                self.app_state.ax.plot([], [], '-', color=color, label=group, linewidth=2)
            self.app_state.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

            # Updates the figure on the GUI
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating biplot: {str(e)}")

    def create_interactive_biplot(self):
        """Create an interactive biplot visualization."""
        # Runs PCA analysis and gets relavent values
        scores, loadings, variance, eigenvals, feat_names = self.get_pca_data()

        # Calculates other need information based on the PCA Resulats
        top_idx, loading_magnitudes, num_feat = self.get_top_pca_features(loadings)
        top_feat = self.app_state.df.columns[top_idx]

        try:
            self.app_state.fig = go.Figure()

            # Calculate axis limits with margin
            scaled_loadings = self.scale_loadings(eigenvals, loadings)

            self.add_interactive_biplot_groups(top_feat, top_idx, feat_names, loading_magnitudes, scaled_loadings)

            self.add_biplot_interactivity(top_idx, loading_magnitudes)
            
            self.update_interactie_biplot_layout(variance)

            file_name = self.save_interactive_plot()
            messagebox.showinfo("Sucess", f"Interactive pca plot sucessfully created: {file_name}")

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")

    def plot_top_features_loadings(self):
        """Plot top feature loadings using LoadingsProcessor."""
        if not self.app_state.df_cleaned.get():
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Get top N features from user input
            top_n = self.app_state.top_n_feat.get()

            # Validate and retrieve loadings
            loadings, focus_columns = self.validate_and_get_loadings(
                heatmap_mode=f"Top {top_n} Features"  # Adjust dynamically
            )

            # Clear the canvas and reinitialize the figure and axes
            self.app_state.fig.clear()  # Clears the existing figure
            self.app_state.ax = self.app_state.fig.add_subplot(111)  # Create a new subplot

            # Plot top feature loadings
            self.app_state.ax.barh(
                focus_columns,
                np.abs(loadings[:len(focus_columns), 0]),  # Example: loadings for PC1
                color='steelblue',
                alpha=0.8
            )
            self.app_state.ax.set_title(f"Top {top_n} Features - Absolute Loadings", fontsize=14)
            self.app_state.ax.set_xlabel("Absolute Loadings", fontsize=12)
            self.app_state.ax.set_ylabel("Features", fontsize=12)
            self.app_state.ax.tick_params(axis='x', labelsize=10)
            self.app_state.ax.tick_params(axis='y', labelsize=10)

            # Updates the figure on the GUI
            self.app_state.main.update_figure()
            messagebox.showinfo("Success", f"Top {top_n} feature loadings plotted successfully!")

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Failed to plot top feature loadings: {str(e)}")


    #### 3. UTILITY METHODS ####

    def upload_mapping_csv(self):
        """Allow the user to upload a mapping CSV file for feature-to-group mapping."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            messagebox.showerror("Error", "No file selected. Please upload a valid mapping CSV.")
            return

        try:
            # Load the CSV into a DataFrame
            df = pd.read_csv(file_path)

            # Validate input DataFrame
            if 'Feature' not in df.columns.to_list() or 'Group' not in df.columns.to_list():
                messagebox.showerror("Error", "Invalid Feature File, 'Feature' or 'Group' column not found")
                return

            # Create feature-to-group mapping and standardize to lowercase
            self.app_state.feat_map = {
                key.lower(): value for key, value in zip(df['Feature'], df['Group'])
            }

            # Get unique groups
            unique_groups = sorted(df['Group'].unique())

            # Generate a dynamic color palette for groups
            colormap = cm.get_cmap('tab20', len(unique_groups))  # Use a colormap with sufficient distinct colors
            self.app_state.feat_colors = {
                group: to_hex(colormap(i)) for i, group in enumerate(unique_groups)
            }

            self.app_state.mapping_uploaded.set(True)

            messagebox.showinfo("Success", "Feature-to-Group mapping loaded successfully.")
        
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")


    #### 4. UI UPDATE METHODS ####

    def toggle_feature_grouping(self):
        """Toggle the feature grouping functionality."""
        if self.enable_feature_grouping.get():
            # Enable the mapping upload button
            self.mapping_button.config(state="normal")
            messagebox.showinfo("Feature Grouping Enabled",
                                "Feature grouping is now enabled. Please upload a mapping file.")
        else:
            # Disable the mapping upload button and reset group-related variables
            self.app_state.mapping_uploaded.set(False)
            self.app_state.feat_map = None
            self.app_state.feat_colors = None

            # Clear results or mapping display
            if hasattr(self, 'feature_results_summary') and self.feature_results_summary is not None:
                self.feature_results_summary.config(state="normal")
                self.feature_results_summary.delete(1.0, tk.END)
                self.feature_results_summary.config(state="disabled")

            messagebox.showinfo("Feature Grouping Disabled", "Feature grouping has been disabled.")

    def init_scree_fig(self):
        # Create scree plot - exact match to original
        self.app_state.fig = Figure(self.app_state.fig_size)
        self.app_state.ax = self.app_state.fig.add_subplot(111)

        # Labels and title - exact match
        self.app_state.ax.set_xlabel('Principal Component Index')
        self.app_state.ax.set_ylabel('Explained Variance Ratio')
        self.app_state.ax.set_title('Scree Plot')

    def init_biplot_fig(self, explained_variance, num_features):
        try:
            # Generates and configures plot appearance
            self.app_state.fig = Figure(self.app_state.fig_size)
            self.app_state.ax = self.app_state.fig.add_subplot(111)
            self.app_state.ax.grid(True, linestyle='--', alpha=0.3)
            self.app_state.ax.set_facecolor('#f8f9fa')
            self.app_state.ax.set_xlabel(f"PC1 ({explained_variance[0]:.1%} explained var.)")
            self.app_state.ax.set_ylabel(f"PC2 ({explained_variance[1]:.1%} explained var.)")
            self.app_state.ax.set_title(f"Biplot with Top {num_features} Significant Features")
            self.app_state.ax.set_aspect('equal', adjustable='box')
            return True
        except Exception:
            return False

    def set_biplot_axis_limits(self, scaled_loadings, top_idx):
        x_min, x_max = np.min(scaled_loadings[top_idx, 0]), np.max(scaled_loadings[top_idx, 0])
        y_min, y_max = np.min(scaled_loadings[top_idx, 1]), np.max(scaled_loadings[top_idx, 1])
        margin = 0.2 * max(x_max - x_min, y_max - y_min)  # 20% margin of the larger range
        self.app_state.ax.set_xlim(x_min - margin, x_max + margin)
        self.app_state.ax.set_ylim(y_min - margin, y_max + margin)
        return scaled_loadings

    def add_biplot_arrows(self, top_feat, top_idx, feat_names, magnitudes, scaled_loadings):
        # Text annotations
        texts = []

        # Generates a generic color mapping if one hasn't been uploaded
        feat_map, feat_colors = self.get_color_mapping(top_feat)

        # Use the color mapping to add arrows to the plot
        for idx in top_idx:
            feature = feat_names[idx]
            magnitude = magnitudes[idx]

            if magnitude < 0.2:
                continue

            group = feat_map.get(feature)
            color = feat_colors.get(group)

            self.app_state.ax.quiver(
                0, 0,
                scaled_loadings[idx, 0],
                scaled_loadings[idx, 1],
                angles='xy',
                scale_units='xy',
                scale=1,
                color=color,
                alpha=0.8,
                width=0.005,
                headwidth=3,
                headlength=5
            )
            
            # Gets user information for plot
            text_dist = self.app_state.text_dist.get()

            text = self.app_state.ax.text(
                scaled_loadings[idx, 0] * text_dist,
                scaled_loadings[idx, 1] * text_dist,
                feature,
                fontsize=10,
                color=color,
                ha='center',
                va='center'
            )
            texts.append(text)

        # Settings to control the text around arrows on the plot?
        adjust_text(
            texts,
            arrowprops=dict(
                arrowstyle='->',
                color='gray',
                alpha=0.5,
                lw=0.5,
                shrinkA=10,  # Moves arrowhead away from text
                shrinkB=10  # Moves arrow tail away from origin
            ),
            force_text=1.5,  # Increased repulsion force to avoid overlaps
            force_points=0.8,  # Avoid overlapping with points
            expand_text=(1.5, 1.5),  # More spacing between labels
            expand_points=(1.2, 1.2),  # Ensure spacing from points
            lim=500  # Higher limit for iterations if overlaps persist
        )

    def add_interactive_biplot_groups(self, top_feat, top_idx, feat_names, magnitudes, scaled_loadings):
        # Generates a generic color mapping if one hasn't been uploaded
        feat_map, feat_colors = self.get_color_mapping(top_feat)

        # Add grouped features - exact match
        legend_groups = set()
        for idx in top_idx:
            feature = feat_names[idx]
            magnitude = magnitudes[idx]

            if magnitude < 0.2:
                continue

            group = feat_map.get(feature)
            color = feat_colors.get(group)

            showlegend = group not in legend_groups
            legend_groups.add(group)

            self.app_state.fig.add_trace(go.Scatter(
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

    def add_biplot_interactivity(self, top_idx, loading_magnitudes):
        fig = self.app_state.fig

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
                        args=[{"visible": [abs(loading_magnitudes[i]) > t for i in range(len(top_idx))]}],
                        label=f"{t:.1f}"
                    ) for t in np.linspace(0, 1, 10)
                ],
                "currentvalue": {"prefix": "Significance Threshold: "}
            }]
        )

    def update_interactie_biplot_layout(self, variance):
        # Update layout - matching original
        self.app_state.fig.update_layout(
            title=f"Interactive Biplot with Top {self.app_state.top_n_feat.get()} Significant Features",
            xaxis_title=f"PC1 ({variance[0]:.1%} explained var.)",
            yaxis_title=f"PC2 ({variance[1]:.1%} explained var.)",
            clickmode='event+select',
            showlegend=True,
            legend=dict(
                title="Feature Groups" if self.app_state.mapping_uploaded.get() else "Features",
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor="rgba(255, 255, 255, 0.8)"
            )
        )
    

    #### 5. Other Functions    ####

    def validate_and_get_loadings(self, heatmap_mode, focus_entry=None):
        """
        Validates PCA model and retrieves loadings based on mode.

        Args:
            heatmap_mode (str): Mode to determine which features to focus on.
            focus_entry (str): Comma-separated column names for custom focus (optional).

        Returns:
            Tuple[np.ndarray, List[str]]: Loadings array and list of focus columns.
        """
        # Validate PCA model
        pca_results = self.app_state.pca_results
        if pca_results is None or not hasattr(pca_results, 'components_'):
            messagebox.showerror("Error", "Please run PCA analysis first.")
            return None, None

        try:
            # Extract loadings
            loadings = pca_results["loadings"]
            feature_scores = np.abs(loadings[:, 0])  # Example: PC1 loadings

            # Determine focus columns based on mode
            if "Top" in heatmap_mode:
                top_n = int(heatmap_mode.split()[1])  # Extract number from mode
                top_indices = np.argsort(feature_scores)[::-1][:top_n]
                focus_columns = [self.app_state.df.columns[i] for i in top_indices]
            elif heatmap_mode == "Custom" and focus_entry:
                focus_columns = [col.strip() for col in focus_entry.split(",") if col.strip()]
                if not all(col in self.app_state.df.columns for col in focus_columns):
                    raise ValueError("Some specified columns do not exist in the dataset.")
            else:
                raise ValueError("Invalid heatmap mode or missing focus entry.")

            return loadings, focus_columns

        except Exception as e:
            messagebox.showerror("Error", f"Error processing loadings: {str(e)}")
            return None, None
        
    def validate_biplot_data(self):
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return False

        if self.enable_feature_grouping.get() and not self.app_state.mapping_uploaded.get():
            messagebox.showerror("Error", "Feature Groups is enabled, but a feature group has not been uploaded!")
            return False
        
        return True

    def get_pca_data(self):
        """Runs PCA analysis and gets important pca results"""
        # Ensure that PCA has been run and get results
        self.app_state.main.run_analysis()
        pca_results = self.app_state.pca_results
        
        # Grab important results
        scores = pca_results['transformed_data']
        loadings = pca_results['loadings']
        variance = pca_results['explained_variance']
        feat_names = [name.lower() for name in pca_results['feature_names']]

        # Calculate eigenvalues from results
        eigenvals = variance[:2]

        return scores, loadings, variance, eigenvals, feat_names
    
    def get_top_pca_features(self, loadings):
        """Gets the top results of PCA analysis based on user selected input"""
        # Gets Users number of PCA results
        num_feat = self.app_state.top_n_feat.get()

        # Calculates PCA magnitudes and related component indexes
        magnitudes = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_idx = np.argsort(magnitudes)[::-1][:num_feat]

        return top_idx, magnitudes, num_feat
    
    def create_confidence_elipse(self, eigenvals):
        """Generates a confidence elipse for a set of eigen Values"""
        confidence_ellipse = stats.chi2.ppf(0.95, df=2)
        return Ellipse(
            (0, 0),
            width=2 * np.sqrt(eigenvals[0] * confidence_ellipse),
            height=2 * np.sqrt(eigenvals[1] * confidence_ellipse),
            alpha=0.1, color='gray', linestyle='--'
        )

    def scale_loadings(self, eigenvals, loadings):
        variance_scale = np.sqrt(eigenvals)
        return loadings[:, :2] * variance_scale

    def get_color_mapping(self, top_feat):
        # Generates a generic color mapping if one hasn't been uploaded
        if not self.app_state.mapping_uploaded.get():
            colormap = cm.get_cmap('tab20', len(top_feat))
            self.app_state.feat_map = {feature.lower(): feature for feature in top_feat}
            self.app_state.feat_colors = {
                feature: to_hex(colormap(i)) for i, feature in enumerate(top_feat)
            }
        return self.app_state.feat_map, self.app_state.feat_colors
    
    def save_interactive_plot(self):
        current_time = time.strftime("%Y%m%d-%H%M%S")
        if not os.path.exists(self.app_state.output_dir):
            os.makedirs(self.app_state.output_dir)

        save_path = os.path.join(self.app_state.output_dir, f"Interactive_Biplot_{current_time}.html")
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'editable': True
        }
        plotly.io.write_html(self.app_state.fig, file=save_path, config=config)
        return save_path


