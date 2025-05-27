import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer

from source.visualization.biplot import InteractiveBiplotVisualizer

from source.utils.constant import *


class HeatmapBox(tk.Frame):
    """
    
    """

    def __init__(self, main=None, **kwargs):
        super().__init__(main, **kwargs)

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
        self.heatmap_banner = tk.Label(self,
                                       **BANNER_STYLE)
        
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
        if not self.df_cleaned:
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Reset the canvas
            self.reset_canvas()

            # Retrieve heatmap mode (e.g., from a dropdown)
            heatmap_mode = self.heatmap_mode_var.get()  # Ensure the actual value is retrieved
            if not heatmap_mode:
                raise ValueError("Heatmap mode is not defined.")

            # Calculate PCA loadings
            loadings = self.pca_results["model"].components_.T

            # Determine focus columns
            focus_columns = self.get_focus_columns(heatmap_mode, focus_entry=self.focus_entry.get())

            # Create and display heatmap
            heatmap_visualizer = LoadingsHeatmapVisualizer(self.fig, self.ax)
            heatmap_visualizer.display_loadings_heatmap(
                loadings=loadings,
                data_columns=self.df.columns.tolist(),
                focus_columns=focus_columns,
                cmap="coolwarm"
            )

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def reset_canvas(self):
        """Clear the canvas and reinitialize the figure and axes."""
        if self.fig is None or self.ax is None:
            self.initialize_matplotlib()  # Reinitialize if needed

        # Clear the entire figure
        self.fig.clear()

        # Create a fresh subplot
        self.ax = self.fig.add_subplot(111)

        # Update the canvas to use the cleared figure
        self.canvas.figure = self.fig
        self.canvas.draw()

