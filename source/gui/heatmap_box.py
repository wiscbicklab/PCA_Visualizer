import tkinter as tk
from tkinter import messagebox
import traceback
from matplotlib.figure import Figure
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

from sklearn.impute import SimpleImputer

from source.gui.app_state import AppState
from source.utils.constant import *


class HeatmapBox(tk.Frame):
    """
    
    """

    def __init__(self, main, app_state: AppState, **kwargs):
        super().__init__(main, **kwargs)
        self.app_state = app_state

        self.heatmap_mode_var = tk.StringVar(value="Top 10 Features")

        # Banner
        self.heatmap_banner = None

        # Heatmap Controls
        self.focus_label = None
        self.focus_entry = None
        self.heatmap_mode_label = None
        self.heatmap_mode_menu = None
        self.heatmap_button = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        # Banner
        self.heatmap_banner = tk.Label(self, **BANNER_STYLE, text="Heatmap Section")
        
        # Heatmap Controls
        self.focus_label = tk.Label(self,
                                    text="Columns to Focus On (comma-separated):",
                                    **LABEL_STYLE)
        self.focus_entry = tk.Entry(self,
                                    width=20,
                                    font=LABEL_STYLE["font"])
        self.heatmap_mode_label = tk.Label(self,
                                           text="Select Heatmap Mode:",
                                           **LABEL_STYLE)
        self.heatmap_mode_menu = tk.OptionMenu(
            self,
            self.heatmap_mode_var,
            "Top 10 Features",
            "Top 20 Features",
            "Custom Features"
        )
        self.heatmap_button = tk.Button(
            self,
            text="Plot Heatmap",
            command=self.plot_loadings_heatmap,
            bg="#007ACC",
            fg="white",
            font=LABEL_STYLE["font"]
        )

    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


        # Banners
        self.heatmap_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Heatmap Section
        self.focus_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.focus_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.heatmap_mode_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.heatmap_mode_menu.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.heatmap_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)


    #### 2. VISUALIZATION METHODS ####

    def plot_loadings_heatmap(self):
        """Plot loadings heatmap using user-selected mode."""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Reset the canvas
            self.init_fig()

            # Retrieve heatmap mode (e.g., from a dropdown)
            heatmap_mode = self.heatmap_mode_var.get()  # Ensure the actual value is retrieved
            if not heatmap_mode:
                raise ValueError("Heatmap mode is not defined.")

            # Calculate PCA loadings
            loadings = self.app_state.pca_results["loadings"]

            # Determine focus columns
            focus_columns = self.get_focus_columns(heatmap_mode, focus_entry=self.focus_entry.get())

            # Create and display heatmap
            self.display_loadings_heatmap(
                loadings=loadings,
                data_columns=self.app_state.df.columns.tolist(),
                focus_columns=focus_columns,
                cmap="coolwarm"
            )

            self.app_state.main.update_figure()  # This ensures the new plot appears on the canvas

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def init_fig(self):
        """Clear the canvas and reinitialize the figure and axes."""
        self.app_state.fig = Figure(self.app_state.fig_size)
        self.app_state.ax = self.app_state.fig.add_subplot(111)

        self.app_state.ax.set_title('Loadings Heatmap', fontsize=16)
        self.app_state.ax.tick_params(axis='x', labelsize=12)
        self.app_state.ax.tick_params(axis='y', labelsize=10)
        self.app_state.ax.set_xlabel('Principal Components', fontsize=14)
        self.app_state.ax.set_ylabel('Features', fontsize=14)


    def display_loadings_heatmap(self, loadings, data_columns, focus_columns=None, cmap='viridis'):
        """
        Display a heatmap of loadings with improved design.
        :param loadings: PCA loadings matrix
        :param data_columns: List of all data column names
        :param focus_columns: List of columns to focus on (optional)
        :param cmap: Colormap for heatmap
        """
        if focus_columns is None:
            focus_columns = data_columns  # Default to all columns if none specified

        # Select only the relevant rows from the loadings matrix
        selected_loadings = loadings[[data_columns.index(col) for col in focus_columns], :]

        # Create the heatmap
        plt.figure(figsize=(10, 12))  # Increase figure size for clarity
        sns.heatmap(
            selected_loadings,
            annot=True,  # Add annotations to cells
            fmt=".2f",  # Format numbers
            cmap=cmap,  # Use perceptually uniform colormap
            cbar_kws={'label': 'Absolute Loadings'},  # Single, descriptive colorbar
            xticklabels=[f'PC{i + 1}' for i in range(selected_loadings.shape[1])],
            yticklabels=focus_columns,
            ax=self.app_state.ax
        )

    def get_focus_columns(self, heatmap_mode_var, focus_entry=None):
        """Determine columns to focus on based on heatmap mode."""
        try:
            if heatmap_mode_var == "Top 10 Features":
                return self.app_state.df.columns[:10].tolist()  # Top 10 features by default
            elif heatmap_mode_var == "Top 20 Features":
                return self.app_state.df.columns[:20].tolist()  # Top 20 features by default
            elif heatmap_mode_var == "Custom Features":
                if focus_entry:
                    columns = [col.strip() for col in focus_entry.split(",") if col.strip()]
                    if not columns:
                        raise ValueError("No valid columns specified for custom heatmap.")
                    # Ensure specified columns exist in the data
                    missing_columns = [col for col in columns if col not in self.data.columns]
                    if missing_columns:
                        raise ValueError(f"The following columns are not in the dataset: {', '.join(missing_columns)}")
                    return columns
                else:
                    raise ValueError("No columns specified for custom heatmap.")
            else:
                raise ValueError(f"Invalid heatmap mode: {heatmap_mode_var}")
        except Exception as e:
            messagebox.showerror("Error", f"Error determining focus columns: {str(e)}")
            return None
