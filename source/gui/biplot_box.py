import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
from matplotlib import cm, pyplot as plt
from matplotlib.colors import to_hex
import pandas as pd
import numpy as np
import os, time

from sklearn.impute import SimpleImputer

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from source.visualization.biplot import BiplotVisualizer, InteractiveBiplotVisualizer
from source.gui.app_state  import AppState


from source.utils.constant import *

import source.utils.file_operations as file_ops


class BiplotBox(tk.Frame):
    """
    Creats a space for Biplot generation buttons
    """

    def __init__(self, main, app_state: AppState, **kwargs):
        super().__init__(main, **kwargs)

        self.app_state = app_state

        # Sets up visualization dependencies
        self.biplot_visualizer = BiplotVisualizer()

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
        self.biplot_banner = tk.Label(self, **BANNER_STYLE)
        
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
        if not self.app_state.df_cleaned:
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Create scree plot - exact match to original
            explained_variance = self.app_state.pca_results["explained_variance"]

            # Remove the old plot
            self.app_state.ax.clear()

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

            # Labels and title - exact match
            self.app_state.ax.set_xlabel('Principal Component Index')
            self.app_state.ax.set_ylabel('Explained Variance Ratio')
            self.app_state.ax.set_title('Scree Plot')

            # Updates the figure on the GUI
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating scree plot: {str(e)}")

    def create_biplot(self):
        """Create biplot visualization."""
        if not self.app_state.df_cleaned:
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Delegate to BiplotVisualizer
            biplot_visualizer = BiplotVisualizer(self.app_state.fig, self.app_state.ax)
            biplot_visualizer.create_biplot(
                pca_model=self.app_state.pca_results["model"],
                x_standardized=self.app_state.pca_results['standardized_data'],
                df=self.app_state.df,
                feature_to_group=self.app_state.feature_to_group,
                enable_feature_grouping=self.enable_feature_grouping.get(),
                top_n=self.app_state.top_n_feat.get(),
                text_dist=self.app_state.text_dist.get(),
            )

            # Apply clarity improvements
            self.app_state.ax.grid(True, linestyle='--', alpha=0.3)
            self.app_state.ax.set_facecolor('#f8f9fa')
            self.app_state.ax.set_aspect('equal', adjustable='box')

            # Updates the figure on the GUI
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating biplot: {str(e)}")

    def create_interactive_biplot(self):
        """Create an interactive biplot visualization."""
        if not self.app_state.df_cleaned:
            return

        # Ensures PCA has been run
        self.app_state.main.run_analysis()

        try:
            interactive_visualizer = InteractiveBiplotVisualizer()
            fig = interactive_visualizer.create_interactive_biplot(
                pca_model=self.app_state.pca_results["model"],
                x_standardized=self.app_state.pca_results["standardized_data"],
                data=self.app_state.df,
                top_n_entry=self.app_state.top_n_feat,  # Replace with actual entry for top N
                text_distance_entry=self.app_state.text_dist,  # Replace with actual entry for text distance
                enable_feature_grouping=self.enable_feature_grouping.get(),
                feature_to_group=self.feature_to_group,
            )

            save_path = interactive_visualizer.save_interactive_biplot(fig, OUTPUT_DIR)
            messagebox.showinfo("Success", f"Interactive biplot saved at {save_path}")


        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")

    def plot_top_features_loadings(self):
        """Plot top feature loadings using LoadingsProcessor."""
        if not self.app_state.df_cleaned:
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

            # Load mapping
            self.load_group_mapping(df)

            # Pass mappings to the visualizer
            self.biplot_visualizer.feature_to_group = self.biplot_manager.feature_to_group
            self.biplot_visualizer.group_colors = self.biplot_manager.group_colors

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
            self.feature_to_group = None
            self.feature_groups_colors = None

            # Clear results or mapping display
            if hasattr(self, 'feature_results_summary') and self.feature_results_summary is not None:
                self.feature_results_summary.config(state="normal")
                self.feature_results_summary.delete(1.0, tk.END)
                self.feature_results_summary.config(state="disabled")

            messagebox.showinfo("Feature Grouping Disabled", "Feature grouping has been disabled.")


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




