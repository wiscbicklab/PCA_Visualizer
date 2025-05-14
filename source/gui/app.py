import tkinter as tk
from tkinter import filedialog, messagebox

import chardet
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import platform

from sklearn.impute import SimpleImputer

# Visualization imports
from source.visualization.pca_visualization import PCAVisualizer
from source.visualization.biplot import BiplotVisualizer, InteractiveBiplotVisualizer, BiplotManager
from source.visualization.scree import ScreePlotVisualizer
from source.visualization.heatmap import LoadingsHeatmapVisualizer
from source.visualization.loadings import LoadingsProcessor

# Core functionality imports
from source.analysis.pca import PCAAnalyzer
from source.utils.constant import *
import source.utils.file_operations as file_ops
from source.utils.helpers import generate_color_palette

# Components Imports
from source.gui.load_file_box import LoadFileBox
from source.gui.clean_file_box import CleanFileBox
from source.gui.pca_box import PcaBox

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
        self.init_dependencies()
        self.init_variables()
        self.setup_window()


        # Create the custom component
        self.load_file_box = None
        self.clean_file_box = None
        self.pca_box = None
    

    
        # Analysis Buttons
        self.biplot_button = None
        self.interactive_biplot_button = None
        self.scree_plot_button = None
        self.top_features_button = None

        # Feature Grouping
        self.grouping_checkbox = None
        self.mapping_label = None
        self.mapping_button = None

        self.focus_checkbox = None

        # Results Section
        self.data_insight_label = None
        self.data_insight_summary = None
        self.featureresults_summary = None

        # Heatmap Controls
        self.focus_label = None
        self.focus_entry = None
        self.heatmap_mode_label = None
        self.heatmap_mode_menu = None
        self.heatmap_button = None

        # Banners
        self.biplot_banner = None
        self.heatmap_banner = None

        # Save Button
        self.save_button = None

        # Sets selected color pallet
        self.selected_palette = tk.StringVar(value="Default")


        # Set up the application
        self.initialize_matplotlib()
        self.create_widgets()
        self.setup_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_window(self):
        """
        Configure the main window.
            Set the window to fullscreen and sets a minimum application size
            Sets a title and background color
        """
        self.title("PCA Analysis Tool")

        # Sets state maximized if possible
        if self.os_type == "Windows" or self.os_type == "Darwin":
            self.state("-zoomed")
        else: self.state('normal')

        self.configure(bg="#f5f5f5")
        self.minsize(1000, 600)

    def initialize_matplotlib(self):
        """Initialize the Matplotlib figure, axes, and canvas."""
        self.fig = Figure(figsize=(5, 5))
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_widget = self.canvas.get_tk_widget()

        self.canvas_widget.grid(
            row=0, column=2, rowspan=25, padx=10, pady=10, sticky="nsew"
        )

    def create_widgets(self):
        """Create all widgets"""

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


        # Input box for custom target
        self.custom_target_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=20, state="disabled")

        # Trace dropdown to enable/disable custom target input
        self.target_mode.trace_add("write", self.update_target_input)

        # Analysis Buttons
        self.biplot_button = tk.Button(self,
                                       text="Biplot with Groups",
                                       **BUTTON_STYLE,
                                       command=self.create_biplot)
        self.interactive_biplot_button = tk.Button(self,
                                                   text="Interactive Biplot",
                                                   **BUTTON_STYLE,
                                                   command=self.create_interactive_biplot)
        self.scree_plot_button = tk.Button(self,
                                           text="Show Scree Plot",
                                           **BUTTON_STYLE,
                                           command=self.create_scree_plot)
        self.top_features_button = tk.Button(self,
                                             text="Top Features Loadings",
                                             **BUTTON_STYLE,
                                             command=self.plot_top_features_loadings)

        # Color Palette Selection
        self.palette_label = tk.Label(self,
                                      text="Select Color Palette:",
                                      bg=LABEL_STYLE["bg"], font=LABEL_STYLE["font"])
        self.palette_menu = tk.OptionMenu(self,
                                          self.selected_palette,
                                          *COLOR_PALETTES.keys(),
                                          command=self.update_color_palette)

        # Feature Grouping Section
        self.grouping_checkbox = tk.Checkbutton(
            self,
            text="Enable Feature Grouping",
            variable=self.enable_feature_grouping,
            bg=LABEL_STYLE["bg"],
            font=LABEL_STYLE["font"],
            command=self.toggle_feature_grouping
        )

        self.mapping_label = tk.Label(self,
                                      text="Feature-to-Group Mapping (Optional):",
                                      bg=LABEL_STYLE["bg"],
                                      font=LABEL_STYLE["font"])

        self.mapping_button = tk.Button(self,
                                        text="Upload Mapping CSV",
                                        **BUTTON_STYLE,
                                        command=self.upload_mapping_csv)
        self.mapping_button.config(state="normal")


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

        # Heatmap Controls
        self.focus_label = tk.Label(self,
                                    text="Columns to Focus On (comma-separated):",
                                    bg=LABEL_STYLE["bg"],
                                    font=LABEL_STYLE["font"])

        self.focus_entry = tk.Entry(self,
                                    width=20,
                                    font=LABEL_STYLE["font"])

        self.heatmap_mode_label = tk.Label(self,
                                           text="Select Heatmap Mode:",
                                           bg=LABEL_STYLE["bg"],
                                           font=LABEL_STYLE["font"])

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


        # Banners
        
        self.biplot_banner = tk.Label(self,
                                      text="Biplot Section",
                                      font=("Helvetica", 12),
                                      bg="#dcdcdc",
                                      relief="groove")
        self.heatmap_banner = tk.Label(self,
                                       text="Heatmap Section",
                                       font=("Helvetica", 12),
                                       bg="#dcdcdc",
                                       relief="groove")
        # Save
        self.save_button = tk.Button(self,
                                     text="Save Plot",
                                     **BUTTON_STYLE,
                                     command=self.save_plot)

    def setup_layout(self):
        """Setup the layout of GUI components"""
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=5)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Place canvas on right side
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=25,
                                         padx=10, pady=10, sticky="nsew")
        
        self.load_file_box.grid(row=0, column=0, padx=10, pady=10, columnspan=2)
        self.clean_file_box.grid(row=1, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        self.pca_box.grid(row=2, column=0, padx=10, pady=10, columnspan=2, sticky="we")
        
        
        # Results Section
        self.data_insight_label.grid(row=27, column=2, padx=5, pady=5, sticky="")
        self.data_insight_summary.grid(row=28, column=2, padx=5, pady=5, sticky="nsew")

        # Visualization Buttons
        self.scree_plot_button.grid(row=25, column=0, padx=5, pady=5)
        self.biplot_button.grid(row=25, column=1, padx=5, pady=5)
        self.interactive_biplot_button.grid(row=26, column=0, padx=5, pady=5)
        self.top_features_button.grid(row=26, column=1, padx=5, pady=5)

        # Banners
        self.biplot_banner.grid(row=21, column=0, columnspan=2, sticky="we", padx=5, pady=5)
        self.heatmap_banner.grid(row=27, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Feature Grouping Section
        self.grouping_checkbox.grid(row=22, column=0, sticky="w", padx=5, pady=5)
        # self.mapping_label.grid(row=21, column=1, padx=5, pady=5, sticky="e")
        self.mapping_button.grid(row=23, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.palette_label.grid(row=24, column=0, padx=5, pady=5, sticky="e")
        self.palette_menu.grid(row=24, column=1, padx=5, pady=5, sticky="w")
        # Initialize `focus_on_loadings` value
        self.focus_checkbox.grid(row=25, column=1, padx=5, pady=5, sticky="e")

        # Heatmap Section
        self.focus_label.grid(row=28, column=0, padx=5, pady=5, sticky="e")
        self.focus_entry.grid(row=28, column=1, padx=5, pady=5, sticky="w")
        self.heatmap_mode_label.grid(row=29, column=0, padx=5, pady=5, sticky="e")
        self.heatmap_mode_menu.grid(row=29, column=1, padx=5, pady=5, sticky="w")
        self.heatmap_button.grid(row=30, column=0, columnspan=2, padx=5, pady=5)
        self.output_dir_label.grid(row=31, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        self.output_dir_button.grid(row=31, column=2, padx=5, pady=5, sticky="e")

        # Save Button
        self.save_button.grid(row=31, column=2, padx=5, pady=5)

        # Configure remaining row weights
        for i in range(31):
            self.grid_rowconfigure(i, weight=1)

    def init_dependencies(self):
        """
        Intializes program dependencies

        ARGS:
            root: The main tkinter windows to build the application on
        """
        self.pca_analyzer = PCAAnalyzer()
        self.biplot_visualizer = BiplotVisualizer()
        self.biplot_manager = BiplotManager()


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
        self.enable_feature_grouping = tk.BooleanVar(value=False)
        self.heatmap_mode_var = tk.StringVar(value="Top 10 Features")
        self.target_mode = tk.StringVar(value="Select Target")

        # Gets the name of the os
        self.os_type = platform.system()



    #### 1. DATA HANDLING METHODS ####

    def run_analysis(self):
        """Execute PCA analysis."""
        if not self.df_clean or not self.df_updated:
            return

        try:
            # Get analysis parameters
            n_components = int(self.components_entry.get())
            self.drop_cols()

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

    

    #### 2. VISUALIZATION METHODS ####

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
        
    def create_scree_plot(self):
        """Create scree plot."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Reset the canvas
            self.reset_canvas()

            scree_visualizer = ScreePlotVisualizer(self.fig, self.ax)
            scree_visualizer.create_scree_plot(self.pca_results["model"])

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating scree plot: {str(e)}")

    def create_biplot(self):
        """Create biplot visualization."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Ensure figure and canvas are properly initialized
            if self.fig is None:
                self.reset_canvas()

            # Reset the canvas before plotting
            self.reset_canvas()

            # Validate and retrieve user inputs
            try:
                top_n = int(self.top_n_entry.get())
            except ValueError:
                top_n = 10  # Default to 10 if invalid input

            try:
                text_dist = float(self.text_distance_entry.get())
            except ValueError:
                text_dist = 1.1  # Default to 1.1 if invalid input


            # Delegate to BiplotVisualizer
            biplot_visualizer = BiplotVisualizer(self.fig, self.ax)
            biplot_visualizer.create_biplot(
                pca_model=self.pca_results["model"],
                x_standardized=self.pca_results['standardized_data'],
                df=self.df,
                feature_to_group=self.feature_to_group,
                enable_feature_grouping=self.enable_feature_grouping.get(),
                top_n=top_n,
                text_dist=text_dist,
                focus_on_loadings=self.focus_on_loadings.get()
            )

            # Apply clarity improvements
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.ax.set_facecolor('#f8f9fa')
            self.ax.set_aspect('equal', adjustable='box')

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating biplot: {str(e)}")

    def create_interactive_biplot(self):
        """Create an interactive biplot visualization."""
        if not self.df_clean:
            return

        # Ensures PCA has been run
        self.run_analysis()

        try:
            

            interactive_visualizer = InteractiveBiplotVisualizer()
            fig = interactive_visualizer.create_interactive_biplot(
                pca_model=self.pca_results["model"],
                x_standardized=self.pca_results["standardized_data"],
                data=self.df,
                top_n_entry=self.components_entry,  # Replace with actual entry for top N
                text_distance_entry=self.components_entry,  # Replace with actual entry for text distance
                enable_feature_grouping=self.enable_feature_grouping.get(),
                feature_to_group=self.feature_to_group,
            )

            save_path = interactive_visualizer.save_interactive_biplot(fig, OUTPUT_DIR)
            messagebox.showinfo("Success", f"Interactive biplot saved at {save_path}")


        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")

    def plot_loadings_heatmap(self):
        """Plot loadings heatmap using user-selected mode."""
        if not self.df_clean:
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

    def plot_top_features_loadings(self):
        """Plot top feature loadings using LoadingsProcessor."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Reset the canvas
            self.reset_canvas()

            # Initialize LoadingsProcessor
            loadings_processor = LoadingsProcessor(self.pca_results["model"], self.df)

            # Get top N features from user input
            try:
                top_n = int(self.top_n_entry.get())
            except ValueError:
                top_n = 10  # Default value if user input is invalid

            # Validate and retrieve loadings
            loadings, focus_columns = loadings_processor.validate_and_get_loadings(
                heatmap_mode=f"Top {top_n} Features"  # Adjust dynamically
            )

            if loadings is None or not focus_columns:
                return  # Error already handled in LoadingsProcessor

            # Clear the canvas and reinitialize the figure and axes
            self.fig.clear()  # Clears the existing figure
            self.ax = self.fig.add_subplot(111)  # Create a new subplot

            # Plot top feature loadings
            self.ax.barh(
                focus_columns,
                np.abs(loadings[:len(focus_columns), 0]),  # Example: loadings for PC1
                color='steelblue',
                alpha=0.8
            )
            self.ax.set_title(f"Top {top_n} Features - Absolute Loadings", fontsize=14)
            self.ax.set_xlabel("Absolute Loadings", fontsize=12)
            self.ax.set_ylabel("Features", fontsize=12)
            self.ax.tick_params(axis='x', labelsize=10)
            self.ax.tick_params(axis='y', labelsize=10)

            # Update the canvas to reflect the new plot
            self.canvas.draw()  # This ensures the new plot appears on the canvas
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

            # Load mapping into BiplotManager
            self.biplot_manager.load_group_mapping(df)

            # Pass mappings to the visualizer
            self.biplot_visualizer.feature_to_group = self.biplot_manager.feature_to_group
            self.biplot_visualizer.group_colors = self.biplot_manager.group_colors

            messagebox.showinfo("Success", "Feature-to-Group mapping loaded successfully.")
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")

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
            if hasattr(self, 'featureresults_summary'):
                self.featureresults_summary.config(state="normal")
                self.featureresults_summary.delete(1.0, tk.END)
                self.featureresults_summary.config(state="disabled")

            messagebox.showinfo("Feature Grouping Disabled", "Feature grouping has been disabled.")

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