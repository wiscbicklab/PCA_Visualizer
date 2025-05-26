import tkinter as tk
from tkinter import VERTICAL, Scrollbar, filedialog, messagebox

import chardet
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
from source.gui.app_state  import AppState

import traceback


class PCAAnalysisApp(tk.Tk):
    """GUI Application for PCA Analysis."""

    def __init__(self):
        """
        Initialize the GUI_Application

        Args:
            root: 
        """
        # Sets up the window, and creates a way to track the app state
        super().__init__()
        self.app_state = AppState(self)
        self.setup_window()

        # Object for running PCA analysis
        self.pca_analyzer = PCAAnalyzer()

        # Creates a scroll bar
        self.options_scroll = None
        self.options_canvas = None
        self.options_window = None
        self.options_frame = None

        # Declare the custom component
        self.load_file_box = None
        self.clean_file_box = None
        self.pca_box = None
        self.biplot_box = None
        self.heatmap_box = None

        # Declare space for the figure to be stored
        self.plot_canvas = None
        self.plot_canvas_figure = None

        # Results Section
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
        if self.app_state.os_type == "Windows" or self.app_state.os_type == "Darwin":
            self.state("-zoomed")
        else: self.state('normal')

        self.configure(bg="#f5f5f5")
        self.minsize(1300, 700)

    def create_widgets(self):
        """Create all widgets"""

        self.plot_canvas = FigureCanvasTkAgg(self.app_state.fig, master=self)
        self.plot_canvas_figure = self.plot_canvas.get_tk_widget()

        # Sets up scrollable window
        self.options_canvas = tk.Canvas(self)
        self.options_scroll = Scrollbar(self, orient=VERTICAL, command=self.options_canvas.yview)
        self.options_canvas.configure(yscrollcommand=self.options_scroll.set)
        self.options_frame = tk.Frame(self.options_canvas, bg="#f0f0f0")
        self.options_window = self.options_canvas.create_window(
            (0, 0),
            window=self.options_frame,
            anchor="nw",
            tags="options_frame"
        )
        self.options_canvas.bind(
            "<Configure>",
            lambda e: [
                self.options_canvas.configure(scrollregion=self.options_canvas.bbox("all")),
                self.options_canvas.itemconfig("options_frame", width=e.width)
            ]
        )
        # Bind mouse wheel scrolling (cross-platform)
        self.options_canvas.bind("<Enter>", lambda e: self._bind_mousewheel())
        self.options_canvas.bind("<Leave>", lambda e: self._unbind_mousewheel())



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
        self.load_file_box = LoadFileBox(self.options_frame, self.app_state, bg="#f0f0f0")
        self.clean_file_box = CleanFileBox(self.options_frame, self.app_state, bg="#f0f0f0")
        self.pca_box = PcaBox(self.options_frame, self.app_state, bg="#f0f0f0")
        self.biplot_box = BiplotBox(self.options_frame, self.app_state, bg="#f0f0f0")
        self.heatmap_box = HeatmapBox(self.options_frame, bg="#f0f0f0")

        # Color Palette Selection
        self.palette_label = tk.Label(self.options_frame,
                                      text="Select Color Palette:",
                                      bg=LABEL_STYLE["bg"], font=LABEL_STYLE["font"])
        self.palette_menu = tk.OptionMenu(self.options_frame,
                                          self.selected_palette,
                                          *COLOR_PALETTES.keys(),
                                          command=self.update_color_palette)

        ### Focus on signficant loadings (Biplot)
        # Create a BooleanVar for the checkbox
        self.focus_on_loadings = tk.BooleanVar(value=True)

        # Results Section
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
        # Configure grid weights
        for i in range(5):
            self.grid_rowconfigure(i, weight=1)
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=0)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)

        # Adds plot and scrollable
        self.options_canvas.grid(row=0, column=0, rowspan=5, padx=10, pady=10, sticky="nswe")
        self.options_scroll.grid(row=0, column=1, rowspan=5, sticky="nsew")
        self.plot_canvas_figure.grid(row=0, column=2, rowspan=3, columnspan=2, padx=10, pady=10, sticky="nsw")
        
        # Sets up custom Components
        self.load_file_box.grid(row=0, column=0, padx=10, pady=10, sticky="we")
        self.clean_file_box.grid(row=1, column=0, padx=10, pady=10, sticky="we")
        self.pca_box.grid(row=2, column=0, padx=10, pady=10, sticky="we")
        self.biplot_box.grid(row=3, column=0, padx=10, pady=10, sticky="we")
        self.heatmap_box.grid(row=4, column=0, padx=10, pady=10, sticky="we")

        # Feature Grouping Section/ Palette Colors
        self.palette_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.palette_menu.grid(row=6, column=0, padx=5, pady=5, sticky="w")
        
        # Results Section
        self.data_insight_summary.grid(row=3, column=2, columnspan=2, padx=5, pady=5, sticky="ew")

        # Save Button
        self.save_button.grid(row=4, column=2, padx=5, pady=5, sticky="w")

        # Output Directory
        self.output_dir_label.grid(row=4, column=3, padx=5, pady=5, sticky="w")
        self.output_dir_button.grid(row=4, column=3, padx=5, pady=5, sticky="e")

        

    

    #### 1. DATA HANDLING METHODS ####

    def run_analysis(self):
        """Execute PCA analysis."""
        # Skip analysis if data isn't cleaned or if data has not changed
        if not self.app_state.df_cleaned or not self.app_state.df_updated:
            return

        try:
            # Run analysis and store the result
            self.app_state.pca_results = self.pca_analyzer.analyze(
                df=self.app_state.df,
                n_components=self.app_state.num_pca_components.get(),
            )

            # Update display
            self.update_results_display(self.app_state.pca_results)

            # Update df status variables
            self.app_state.df_updated = False

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
                return self.app_state.df.columns[:10].tolist()  # Top 10 features by default
            elif heatmap_mode_var == "Top 20 Features":
                return self.app_state.df.columns[:20].tolist()  # Top 20 features by default
            elif heatmap_mode_var == "Custom Features":
                if focus_entry:
                    columns = [col.strip() for col in focus_entry.split(",") if col.strip()]
                    if not columns:
                        raise ValueError("No valid columns specified for custom heatmap.")
                    # Ensure specified columns exist in the data
                    missing_columns = [col for col in columns if col not in self.app_state.df.columns]
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

  
    #### 4. UI UPDATE METHODS ####

    def update_data_info(self):
        """Update display with simplified data information."""
        if self.app_state.df_loaded:
            # Simple, clean formatting
            info_text = "Data Information\n"
            info_text += "═══════════════\n\n"
            info_text += f"Dataset Shape: {self.app_state.df.shape[0]} rows × {self.app_state.df.shape[1]} columns\n\n"
            info_text += "Columns:\n"

            # Simple column listing
            columns = self.app_state.df.columns.tolist()
            for i, col in enumerate(columns, 1):
                info_text += f"{i}. {col}\n"

            # Update the results summary box
            self.data_insight_summary.delete(1.0, tk.END)
            self.data_insight_summary.insert(tk.END, info_text)
            
            # Generate new Blank figure
            old_figsize = self.app_state.fig.get_size_inches()
            self.app_state.fig = Figure(figsize=old_figsize)
            self.app_state.ax = self.app_state.fig.add_subplot(111)
            self.app_state.ax.grid(True)

            self.app_state.main.update_figure() 

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


    def update_figure(self):
        # Destroy old canvas widget if it exists
        self.app_state.main.plot_canvas_figure.delete("all")

        # Create new canvas with updated figure
        self.app_state.main.plot_canvas = FigureCanvasTkAgg(self.app_state.fig, master=self.app_state.main)
        self.app_state.main.plot_canvas.draw()

        # Get the Tkinter widget and add it to the grid
        self.app_state.main.plot_canvas_figure = self.app_state.main.plot_canvas.get_tk_widget()
        self.app_state.main.plot_canvas_figure.grid(row=0, column=2, rowspan=3, columnspan=2, padx=10, pady=10, sticky="nsw")



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
        if self.plot_canvas:
            self.plot_canvas.get_tk_widget().destroy()
        plt.close('all')
        self.destroy()

    def _bind_mousewheel(self):
        # Windows and macOS
        self.options_canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        # Linux
        self.options_canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.options_canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _unbind_mousewheel(self):
        self.options_canvas.unbind_all("<MouseWheel>")
        self.options_canvas.unbind_all("<Button-4>")
        self.options_canvas.unbind_all("<Button-5>")

    def _on_mousewheel(self, event):
        if event.num == 4:  # Linux scroll up
            self.options_canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.options_canvas.yview_scroll(1, "units")
        else:  # Windows/macOS
            self.options_canvas.yview_scroll(-1 * (event.delta // 120), "units")


# Start App
if __name__ == "__main__":   
        app = PCAAnalysisApp()  
        app.mainloop()