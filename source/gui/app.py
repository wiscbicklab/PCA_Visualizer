import tkinter as tk
from tkinter import filedialog, messagebox

import chardet
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure

import pandas as pd
import numpy as np
import platform

from sklearn.impute import SimpleImputer




# Core functionality imports
from source.analysis.pca import PCAAnalyzer
from source.utils.constant import *
import source.utils.file_operations as file_ops
from source.utils.helpers import generate_color_palette

# Components Imports
from source.gui.load_file_box import LoadFileBox
from source.gui.clean_file_box import CleanFileBox
from source.gui.pca_box import PcaBox
from source.gui.biplot_box import BiplotBox
from source.gui.heatmap_box import HeatmapBox

import traceback


class PCAAnalysisApp(tk.Tk):
    """GUI Application for PCA Analysis."""

    def __init__(self):
        """
        Initialize the GUI_Application

        Args:
            root: 
        """
        # Sets up the window, object dependencies, and variables
        super().__init__()
        self.init_variables()
        self.setup_window()

        self.fig = None

        self.pca_analyzer = PCAAnalyzer()

        # Declare the custom component
        self.load_file_box = None
        self.clean_file_box = None
        self.pca_box = None
        self.biplot_box = None
        self.heatmap_box = None

        self.focus_checkbox = None

        # Results Section
        self.data_insight_label = None
        self.data_insight_summary = None

        # Save Button
        self.save_button = None

        # Sets selected color pallet
        self.selected_palette = tk.StringVar(value="Default")


        # Set up the application
        #self.initialize_matplotlib()
        self.create_widgets()
        self.setup_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_window(self):
        """
        Configure the main window.
            Set the window to fullscreen or to normal, dependent on os
            Sets a minimum application size
            Sets a title and background color
        """
        self.title("PCA Analysis Tool")

        # Sets state maximized if possible
        if self.os_type == "Windows" or self.os_type == "Darwin":
            self.state("-zoomed")
        else: self.state('normal')

        self.configure(bg="#f5f5f5")
        self.minsize(1000, 600)



    def init_variables(self):
        """
        Initializes variables for storing data within the application
        """
        # Variables for tracking the data to run PCA on
        self.df = None
        self.df_updated = False
        self.df_loaded = False
        self.df_clean = False

        # Variables for visualizing pca results
        self.pca_results = None
        self.feature_to_group = None
        self.feature_groups_colors = None

        # Variables to track user inputs from the GUI
        self.target_var = tk.StringVar(value="None")
        
        self.target_mode = tk.StringVar(value="Select Target")

        # Gets the name of the os
        self.os_type = platform.system()

    def create_widgets(self):
        """Create all widgets"""

        self.fig = Figure(figsize=(5, 5))

        # Output Directory Section
        self.output_dir = OUTPUT_DIR  # Default directory
        self.output_dir_label = tk.Label(self,
                                         text=f"Output Directory: {self.output_dir}",
                                         bg=LABEL_STYLE["bg"],
                                         font=LABEL_STYLE["font"],
                                         wraplength=300,  # Wrap text for long paths
                                         anchor="w", justify="left")
        self.output_dir_button = tk.Button(self,
                                           text="Select Output Directory",
                                           **BUTTON_STYLE,
                                           command=self.select_output_directory)

        # Intialize Custom components
        self.load_file_box = LoadFileBox(self, bg="#f0f0f0")
        self.clean_file_box = CleanFileBox(self, bg="#f0f0f0")
        self.pca_box = PcaBox(self, bg="#f0f0f0")
        self.biplot_box = BiplotBox(self, self.fig, bg="#f0f0f0")
        self.heatmap_box = HeatmapBox(self, bg="#f0f0f0")


        # Input box for custom target
        self.custom_target_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=20, state="disabled")

        # Trace dropdown to enable/disable custom target input
        self.target_mode.trace_add("write", self.update_target_input)

        # Color Palette Selection
        self.palette_label = tk.Label(self,
                                      text="Select Color Palette:",
                                      bg=LABEL_STYLE["bg"], font=LABEL_STYLE["font"])
        self.palette_menu = tk.OptionMenu(self,
                                          self.selected_palette,
                                          *COLOR_PALETTES.keys(),
                                          command=self.update_color_palette)

        ### Focus on signficant loadings (Biplot)
        # Create a BooleanVar for the checkbox
        self.focus_on_loadings = tk.BooleanVar(value=True)

        # Add the "Focus on Loadings" checkbox
        self.focus_checkbox = tk.Checkbutton(
            self,
            text="Focus on Loadings",
            variable=self.focus_on_loadings,
            command=self.update_focus_on_loadings)  # Update logic when toggled

        # Results Section
        self.data_insight_label = tk.Label(self,
                                         text="Data Insights Box:",
                                         **LABEL_STYLE)
        self.data_insight_summary = tk.Text(self,
                                          height=8,
                                          width=50,
                                          font=LABEL_STYLE["font"],
                                          bg="white")

        # Save
        self.save_button = tk.Button(self,
                                     text="Save Plot",
                                     **BUTTON_STYLE,
                                     command=self.save_plot)

    def setup_layout(self):
        """Setup the layout of GUI components"""
        # Adds plot 
        self.canvas_widget.grid(
            row=0, column=2, rowspan=25, padx=10, pady=10, sticky="nsew")

        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=5)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Place canvas on right side
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=25,
                                         padx=10, pady=10, sticky="nsew")
        
        self.load_file_box.grid(row=0, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        self.clean_file_box.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        self.pca_box.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        self.biplot_box.grid(row=3, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        self.heatmap_box.grid(row=4, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        
        # Results Section
        self.data_insight_label.grid(row=27, column=2, padx=5, pady=5, sticky="")
        self.data_insight_summary.grid(row=28, column=2, padx=5, pady=5, sticky="nsew")

        # Feature Grouping Section/ Palette Colors
        self.palette_label.grid(row=24, column=0, padx=5, pady=5, sticky="e")
        self.palette_menu.grid(row=24, column=1, padx=5, pady=5, sticky="w")

        # Initialize `focus_on_loadings` value
        self.focus_checkbox.grid(row=25, column=1, padx=5, pady=5, sticky="e")

        # Heatmap Section left over??? Probably to be fixed
        self.output_dir_label.grid(row=31, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.output_dir_button.grid(row=31, column=2, padx=5, pady=5, sticky="e")

        # Save Button
        self.save_button.grid(row=31, column=2, padx=5, pady=5)

        # Configure remaining row weights
        for i in range(31):
            self.grid_rowconfigure(i, weight=1)

    

    #### 1. DATA HANDLING METHODS ####

    def run_analysis(self, n_components):
        """Execute PCA analysis."""
        # Skip analysis if data isn't cleaned or if data has not changed
        if not self.df_clean or not self.df_updated:
            return

        try:
            # Run analysis and store the result
            self.pca_results = self.pca_analyzer.analyze(
                df=self.df,
                n_components=n_components,
            )

            # Update display
            self.update_results_display(self.pca_results)

            # Update df status variables
            self.df_updated = False

        except ValueError as ve:
            messagebox.showerror("Analysis Error", str(ve))
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"PCA analysis failed: {str(e)}")

    def select_output_directory(self):
        """Allow the user to select an output directory for saving plots."""
        selected_dir = filedialog.askdirectory()
        if selected_dir:  # If the user selects a directory
            self.output_dir = selected_dir
            self.output_dir_label.config(text=f"Output Directory: {self.output_dir}")
            messagebox.showinfo("Directory Selected", f"Output directory set to:\n{self.output_dir}")
        else:
            messagebox.showwarning("No Directory Selected", "Using the default output directory.")
      
    

    #### 3. UTILITY METHODS ####
   
    def get_focus_columns(self, heatmap_mode_var, focus_entry=None):
        """Determine columns to focus on based on heatmap mode."""
        try:
            if heatmap_mode_var == "Top 10 Features":
                return self.df.columns[:10].tolist()  # Top 10 features by default
            elif heatmap_mode_var == "Top 20 Features":
                return self.df.columns[:20].tolist()  # Top 20 features by default
            elif heatmap_mode_var == "Custom Features":
                if focus_entry:
                    columns = [col.strip() for col in focus_entry.split(",") if col.strip()]
                    if not columns:
                        raise ValueError("No valid columns specified for custom heatmap.")
                    # Ensure specified columns exist in the data
                    missing_columns = [col for col in columns if col not in self.df.columns]
                    if missing_columns:
                        raise ValueError(f"The following columns are not in the dataset: {', '.join(missing_columns)}")
                    return columns
                else:
                    raise ValueError("No columns specified for custom heatmap.")
            else:
                raise ValueError(f"Invalid heatmap mode: {heatmap_mode_var}")
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error determining focus columns: {str(e)}")
            return None

    def update_focus_on_loadings(self):
        """
        Update logic or perform actions based on the checkbox state.
        """
        focus_value = self.focus_on_loadings.get()  # Retrieve the value (True/False)


    #### 4. UI UPDATE METHODS ####

    def update_data_info(self):
        """Update display with simplified data information."""
        if self.df_loaded:
            # Simple, clean formatting
            info_text = "Data Information\n"
            info_text += "═══════════════\n\n"
            info_text += f"Dataset Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns\n\n"
            info_text += "Columns:\n"

            # Simple column listing
            columns = self.df.columns.tolist()
            for i, col in enumerate(columns, 1):
                info_text += f"{i}. {col}\n"

            # Update the results summary box
            self.data_insight_summary.delete(1.0, tk.END)
            self.data_insight_summary.insert(tk.END, info_text)

    def update_results_display(self, results: dict):
        """Update results display with simplified formatting."""
        self.data_insight_summary.delete(1.0, tk.END)

        # Simple, clean formatting
        summary = "PCA Analysis Results\n"
        summary += "══════════════════\n\n"

        # Basic Information
        summary += f"Number of components: {results['n_components']}\n"
        summary += f"Original shape: {results['original_shape']}\n"
        summary += f"Prepared shape: {results['prepared_shape']}\n\n"

        # Explained Variance Section
        summary += "Explained Variance Ratios:\n"
        for i, var in enumerate(results['explained_variance']):
            summary += f"PC{i + 1}: {var:.3f}\n"

        self.data_insight_summary.insert(tk.END, summary)

    def update_color_palette(self, *args):
        try:
            if self.feature_to_group:
                unique_groups = set(self.feature_to_group.values())
                n_groups = len(unique_groups)
                selected_palette = self.selected_palette.get()

                # Use predefined preferred colors (if any)
                preferred_colors = {
                    "FAB": "#000000",  # Black
                    "non-FAB": "#C0C0C0",  # Silver
                    "RAA": "#FF0000",  # Red
                    "Beneficials": "#008000",  # Green
                    "non-RAA pests": "#FFC0CB"  # Pink
                }

                # Generate a combined palette using the helper function
                self.feature_groups_colors = generate_color_palette(n_groups, preferred_colors)
            else:
                messagebox.showinfo("No Groups Defined", "No feature groups are currently defined.")
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Failed to update color palette: {str(e)}")

    def update_target_input(self, *args):
        """Enable or disable the target input box based on the dropdown selection."""
        if self.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.delete(0, tk.END)
            self.custom_target_entry.config(state="disabled")


    #### 5. EVENT HANDLERS ####

    def save_plot(self):
        """Save the current plot using the dynamic output directory."""
        try:
            save_path = file_ops.save_plot(self.fig, output_dir=self.output_dir)
            messagebox.showinfo("Success", f"Plot saved at:\n{save_path}")

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Save Error", f"Could not save plot: {str(e)}")

    def on_close(self):
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
        plt.close('all')
        self.destroy()



# Start App
if __name__ == "__main__":   
        app = PCAAnalysisApp()  
        app.mainloop()