import tkinter as tk
from tkinter import filedialog, messagebox

import chardet
from matplotlib import pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import numpy as np
import os
import time

from sklearn.impute import SimpleImputer

# Visualization imports
from source.visualization.pca_visualization import PCAVisualizer
from source.visualization.biplot import BiplotVisualizer, InteractiveBiplotVisualizer, BiplotManager
from source.visualization.scree import ScreePlotVisualizer
from source.visualization.heatmap import LoadingsHeatmapVisualizer
from source.visualization.loadings import LoadingsProcessor

# Core functionality imports
from source.analysis.pca import PCAAnalyzer
from source.utils.constant import OUTPUT_DIR, DEFAULT_COLUMNS_TO_DROP
from source.utils.file_operations import load_file, save_plot
from source.utils.helpers import generate_color_palette


class PCAAnalysisApp:
    """GUI Application for PCA Analysis."""

    def __init__(self, master):
        """Initialize the application."""
        self.master = master
        self.pca_analyzer = PCAAnalyzer()
        self.biplot_visualizer = BiplotVisualizer()
        self.biplot_manager = BiplotManager()

        # Initialize all GUI variables
        self.target_var = tk.StringVar(value="None")
        self.missing_choice = tk.StringVar(value="impute_mean")
        self.bbch_choice = tk.IntVar(value=-1)
        self.enable_feature_grouping = tk.BooleanVar(value=False)
        self.heatmap_mode_var = tk.StringVar(value="Top 10 Features")
        self.target_mode = tk.StringVar(value="Select Target")

        # Initialize all widget references
        # File Section
        self.file_label = None
        self.file_button = None
        self.clean_data_button = None

        # Missing Values Section
        self.missing_label = None
        self.impute_mean_radio = None
        self.impute_median_radio = None
        self.replace_nan_radio = None
        self.leave_empty_radio = None

        # BBCH Selection
        self.bbch_label = None
        self.bbch_none_radio = None
        self.bbch_59_radio = None
        self.bbch_69_radio = None
        self.bbch_85_radio = None

        # Drop Columns Section
        self.drop_label = None
        self.drop_entry = None

        # PCA Parameters
        self.components_label = None
        self.components_entry = None

        # Analysis Buttons
        self.run_button = None
        self.visualize_button = None
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
        self.pcaresults_label = None
        self.pcaresults_summary = None
        self.featureresults_summary = None

        # Heatmap Controls
        self.focus_label = None
        self.focus_entry = None
        self.heatmap_mode_label = None
        self.heatmap_mode_menu = None
        self.heatmap_button = None

        # Banners
        self.clean_data_banner = None
        self.visualizepca_banner = None
        self.biplot_banner = None
        self.heatmap_banner = None

        # Save Button
        self.save_button = None

        # Data-related variables
        self.data = None
        self.pca_model = None
        self.standardized_data = None
        self.feature_to_group = None
        self.feature_groups_colors = None

        # Style constants
        self.button_style = {
            'font': ('Helvetica', 10),
            'bg': '#007ACC',
            'fg': 'white',
            'activebackground': '#005f99',
            'relief': 'raised',
            'width': 18
        }

        self.color_palettes = {
            "Default": {
                "FAB": "black",
                "non-FAB": "silver",
                "non-RAA pests": "pink",
                "Beneficials": "green",
                "RAA": "red"
            },
            "Colorblind-Friendly": {
                "FAB": "#117733",
                "non-FAB": "#88CCEE",
                "non-RAA pests": "#CC6677",
                "Beneficials": "#DDCC77",
                "RAA": "#332288"
            },
            "Bright": {
                "FAB": "#FF0000",
                "non-FAB": "#00FF00",
                "non-RAA pests": "#0000FF",
                "Beneficials": "#FFFF00",
                "RAA": "#FF00FF"
            }
        }
        self.selected_palette = tk.StringVar(value="Default")


        # Set up the application
        self.setup_window()
        self.initialize_matplotlib()
        self.create_widgets()
        self.setup_layout()
        self.disable_visualization_buttons()

    def setup_window(self):
        """Configure the main window."""
        self.master.title("PCA Analysis Tool")
        self.master.geometry("1200x800")
        self.master.configure(bg="#f5f5f5")
        self.master.minsize(1000, 600)

    def initialize_matplotlib(self):
        """Initialize the Matplotlib figure, axes, and canvas."""
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # Attach canvas to Tkinter

    def create_widgets(self):
        """Create all widgets"""
        # File Section
        self.file_label = tk.Label(self.master, text="Load CSV file:",
                                   bg="#f5f5f5", font=('Helvetica', 10))
        self.file_button = tk.Button(self.master, text="Browse",
                                     **self.button_style, command=self.load_file)

        # Output Directory Section
        self.output_dir = OUTPUT_DIR  # Default directory
        self.output_dir_label = tk.Label(self.master,
                                         text=f"Output Directory: {self.output_dir}",
                                         bg="#f5f5f5",
                                         font=('Helvetica', 10),
                                         wraplength=300,  # Wrap text for long paths
                                         anchor="w", justify="left")
        self.output_dir_button = tk.Button(self.master,
                                           text="Select Output Directory",
                                           **self.button_style,
                                           command=self.select_output_directory)

        self.clean_data_button = tk.Button(self.master,
                                           text="Clean CSV",
                                           **self.button_style,
                                           command=self.clean_data)

        # Missing Values Section
        self.missing_label = tk.Label(self.master,
                                      text="Handle Missing Values:",
                                      bg="#f5f5f5",
                                      font=('Helvetica', 10))
        self.impute_mean_radio = tk.Radiobutton(self.master,
                                                text="Impute with Mean",
                                                variable=self.missing_choice,
                                                value="impute_mean",
                                                bg="#f5f5f5")
        self.impute_median_radio = tk.Radiobutton(self.master,
                                                  text="Impute with Median",
                                                  variable=self.missing_choice,
                                                  value="impute_median",
                                                  bg="#f5f5f5")
        self.replace_nan_radio = tk.Radiobutton(self.master,
                                                text="Replace NaN with 0",
                                                variable=self.missing_choice,
                                                value="replace_nan",
                                                bg="#f5f5f5")
        self.leave_empty_radio = tk.Radiobutton(self.master,
                                                text="Leave Empty (Null)",
                                                variable=self.missing_choice,
                                                value="leave_empty",
                                                bg="#f5f5f5")

        # BBCH Selection
        self.bbch_label = tk.Label(self.master,
                                   text="Filter by BBCH Stage:",
                                   bg="#f5f5f5",
                                   font=('Helvetica', 10))
        self.bbch_none_radio = tk.Radiobutton(self.master,
                                              text="All (no filter)",
                                              variable=self.bbch_choice,
                                              value=-1,
                                              bg="#f5f5f5")
        self.bbch_59_radio = tk.Radiobutton(self.master,
                                            text="BBCH 59",
                                            variable=self.bbch_choice,
                                            value=59,
                                            bg="#f5f5f5")
        self.bbch_69_radio = tk.Radiobutton(self.master,
                                            text="BBCH 69",
                                            variable=self.bbch_choice,
                                            value=69,
                                            bg="#f5f5f5")
        self.bbch_85_radio = tk.Radiobutton(self.master,
                                            text="BBCH 85",
                                            variable=self.bbch_choice,
                                            value=85,
                                            bg="#f5f5f5")

        # Drop Columns Section
        self.drop_label = tk.Label(self.master,
                                   text="Columns to Drop (comma-separated):",
                                   bg="#f5f5f5",
                                   font=('Helvetica', 10))
        self.drop_entry = tk.Entry(self.master, width=40, font=('Helvetica', 10))

        # Replace Column Section
        self.replace_label = tk.Label(self.master,
                                      text="Replace Column Name (Correct typos):",
                                      bg="#f5f5f5",
                                      font=('Helvetica', 10))

        self.replace_old_entry = tk.Entry(self.master,
                                          width=20,
                                          font=('Helvetica', 10))
        self.replace_old_entry.insert(0, "Enter current name")  # Placeholder text

        self.replace_new_entry = tk.Entry(self.master,
                                          width=20,
                                          font=('Helvetica', 10))
        self.replace_new_entry.insert(0, "Enter new name")  # Placeholder text

        self.replace_button = tk.Button(self.master,
                                        text="Replace Column Name",
                                        **self.button_style,
                                        command=self.replace_column_name)

        # PCA Parameters Section
        self.components_label = tk.Label(self.master,
                                         text="Number of PCA Components:",
                                         bg="#f5f5f5",
                                         font=('Helvetica', 10))
        self.components_entry = tk.Entry(self.master,
                                         font=('Helvetica', 10),
                                         width=10)
        self.components_entry.insert(0, "2")

        self.top_n_label = tk.Label(self.master, text="Top N Features for Biplot:", bg="#f5f5f5", font=('Helvetica', 10))
        self.top_n_entry = tk.Entry(self.master, font=('Helvetica', 10), width=10)
        self.top_n_entry.insert(0, "10")  # Default to 10

        self.text_distance_label = tk.Label(self.master, text="Text Distance for Labels:", bg="#f5f5f5",
                                            font=('Helvetica', 10))
        self.text_distance_entry = tk.Entry(self.master, font=('Helvetica', 10), width=10)
        self.text_distance_entry.insert(0, "1.1")  # Default to 1.1

        # Dropdown for selecting predefined targets
        self.target_label = tk.Label(self.master, text="Target Variable:", bg="#f5f5f5", font=('Helvetica', 10))
        self.target_mode = tk.StringVar()
        self.target_mode.set("None")  # Default option
        target_options = ["None", "bbch", "Input Specific Target"]
        self.target_dropdown = tk.OptionMenu(self.master, self.target_mode, *target_options)
        self.target_dropdown.config(font=('Helvetica', 10), bg="#007ACC", fg="white",
                                    activebackground="#005f99", relief="flat")

        # Input box for custom target
        self.custom_target_entry = tk.Entry(self.master, font=('Helvetica', 10), width=20, state="disabled")

        # Trace dropdown to enable/disable custom target input
        self.target_mode.trace("w", self.update_target_input)

        # Analysis Buttons
        self.run_button = tk.Button(self.master,
                                    text="Run PCA Analysis",
                                    **self.button_style,
                                    command=self.run_analysis)
        self.visualize_button = tk.Button(self.master,
                                          text="Visualize PCA",
                                          **self.button_style,
                                          command=self.visualize_pca)
        self.biplot_button = tk.Button(self.master,
                                       text="Biplot with Groups",
                                       **self.button_style,
                                       command=self.create_biplot)
        self.interactive_biplot_button = tk.Button(self.master,
                                                   text="Interactive Biplot",
                                                   **self.button_style,
                                                   command=self.create_interactive_biplot)
        self.scree_plot_button = tk.Button(self.master,
                                           text="Show Scree Plot",
                                           **self.button_style,
                                           command=self.create_scree_plot)
        self.top_features_button = tk.Button(self.master,
                                             text="Top Features Loadings",
                                             **self.button_style,
                                             command=self.plot_top_features_loadings)

        # Color Palette Selection
        self.palette_label = tk.Label(self.master,
                                      text="Select Color Palette:",
                                      bg="#f5f5f5", font=('Helvetica', 10))
        self.palette_menu = tk.OptionMenu(self.master,
                                          self.selected_palette,
                                          *self.color_palettes.keys(),
                                          command=self.update_color_palette)

        # Feature Grouping Section
        self.grouping_checkbox = tk.Checkbutton(
            self.master,
            text="Enable Feature Grouping",
            variable=self.enable_feature_grouping,
            bg="#f5f5f5",
            font=('Helvetica', 10),
            command=self.toggle_feature_grouping
        )

        self.mapping_label = tk.Label(self.master,
                                      text="Feature-to-Group Mapping (Optional):",
                                      bg="#f5f5f5",
                                      font=('Helvetica', 10))

        self.mapping_button = tk.Button(self.master,
                                        text="Upload Mapping CSV",
                                        **self.button_style,
                                        command=self.upload_mapping_csv)
        self.mapping_button.config(state="disabled")


        ### Focus on signficant loadings (Biplot)
        # Create a BooleanVar for the checkbox
        self.focus_on_loadings = tk.BooleanVar(value=True)

        # Add the "Focus on Loadings" checkbox
        self.focus_checkbox = tk.Checkbutton(
            self.master,
            text="Focus on Loadings",
            variable=self.focus_on_loadings,
            command=self.update_focus_on_loadings)  # Update logic when toggled

        # Results Section

        self.pcaresults_label = tk.Label(self.master,
                                         text="Data Insights Box:",
                                         bg="#f5f5f5",
                                         font=('Helvetica', 10))
        self.pcaresults_summary = tk.Text(self.master,
                                          height=8,
                                          width=50,
                                          font=('Helvetica', 10),
                                          bg="white")

        # Heatmap Controls
        self.focus_label = tk.Label(self.master,
                                    text="Columns to Focus On (comma-separated):",
                                    bg="#f5f5f5",
                                    font=('Helvetica', 10))

        self.focus_entry = tk.Entry(self.master,
                                    width=20,
                                    font=('Helvetica', 10))

        self.heatmap_mode_label = tk.Label(self.master,
                                           text="Select Heatmap Mode:",
                                           bg="#f5f5f5",
                                           font=('Helvetica', 10))

        self.heatmap_mode_menu = tk.OptionMenu(
            self.master,
            self.heatmap_mode_var,
            "Top 10 Features",
            "Top 20 Features",
            "Custom Features"
        )

        self.heatmap_button = tk.Button(
            self.master,
            text="Plot Heatmap",
            command=self.plot_loadings_heatmap,
            bg="#007ACC",
            fg="white",
            font=('Helvetica', 10)
        )


        # Banners
        self.clean_data_banner = tk.Label(self.master,
                                          text="Clean and/or Filter Data",
                                          font=("Helvetica", 12),
                                          bg="#dcdcdc",
                                          relief="groove")
        self.clean_data_banner = tk.Label(self.master,
                                          text="Clean and/or Filter Data",
                                          font=("Helvetica", 12),
                                          bg="#dcdcdc",
                                          relief="groove")
        self.visualizepca_banner = tk.Label(self.master,
                                            text="Visualize PCA",
                                            font=("Helvetica", 12),
                                            bg="#dcdcdc",
                                            relief="groove")
        self.biplot_banner = tk.Label(self.master,
                                      text="Biplot Section",
                                      font=("Helvetica", 12),
                                      bg="#dcdcdc",
                                      relief="groove")
        self.heatmap_banner = tk.Label(self.master,
                                       text="Heatmap Section",
                                       font=("Helvetica", 12),
                                       bg="#dcdcdc",
                                       relief="groove")
        # Save
        self.save_button = tk.Button(self.master,
                                     text="Save Plot",
                                     **self.button_style,
                                     command=self.save_plot)

    def setup_layout(self):
        """Setup the layout of GUI components"""
        # Configure grid weights
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(2, weight=5)
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=1)

        # Place canvas on right side
        self.canvas.get_tk_widget().grid(row=0, column=2, rowspan=25,
                                         padx=10, pady=10, sticky="nsew")

        # File Selection
        self.file_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.file_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Clean Data Banner
        self.clean_data_banner.grid(row=1, column=0, columnspan=2,
                                    sticky="we", padx=5, pady=5)

        # Missing Values Section
        self.missing_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.impute_mean_radio.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.impute_median_radio.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.replace_nan_radio.grid(row=5, column=0, padx=5, pady=5, sticky="w")
        self.leave_empty_radio.grid(row=6, column=0, padx=5, pady=5, sticky="w")

        # BBCH Selection
        self.bbch_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.bbch_none_radio.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.bbch_59_radio.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.bbch_69_radio.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        self.bbch_85_radio.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Clean Data Button
        self.clean_data_button.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

        # Drop Columns Section
        self.drop_label.grid(row=10, column=0, padx=5, pady=5, sticky="e")
        self.drop_entry.grid(row=10, column=1, padx=5, pady=5, sticky="w")

        # self.replace_label.grid(row=11, column=0, padx=5, pady=5, sticky="e")
        # self.replace_old_entry.grid(row=11, column=1, padx=5, pady=5, sticky="w")
        # self.replace_new_entry.grid(row=12, column=1, padx=5, pady=5, sticky="w")
        # self.replace_button.grid(row=12, column=0, padx=5, pady=5, sticky="e")

        # Target Selection Section
        self.target_label.grid(row=15, column=0, padx=5, pady=5, sticky="w")
        self.target_dropdown.grid(row=15, column=1, padx=5, pady=5, sticky="w")
        self.custom_target_entry.grid(row=16, column=1, padx=5, pady=5, sticky="w")
        # PCA Parameters
        self.components_label.grid(row=17, column=0, padx=5, pady=5, sticky="e")
        self.components_entry.grid(row=17, column=1, padx=5, pady=5, sticky="w")

        self.top_n_label.grid(row=18, column=0, padx=5, pady=5, sticky="e")
        self.top_n_entry.grid(row=18, column=1, padx=5, pady=5, sticky="w")

        self.text_distance_label.grid(row=19, column=0, padx=5, pady=5, sticky="e")
        self.text_distance_entry.grid(row=19, column=1, padx=5, pady=5, sticky="w")

        # Run Analysis Buttons
        self.run_button.grid(row=20, column=0, padx=5, pady=5)
        self.visualize_button.grid(row=20, column=1, padx=5, pady=5)

        # Results Section
        self.pcaresults_label.grid(row=13, column=0, padx=5, pady=5, sticky="w")
        self.pcaresults_summary.grid(row=13, column=1, padx=5, pady=5, sticky="nsew")

        # Visualization Buttons
        self.scree_plot_button.grid(row=25, column=0, padx=5, pady=5)
        self.biplot_button.grid(row=25, column=1, padx=5, pady=5)
        self.interactive_biplot_button.grid(row=26, column=0, padx=5, pady=5)
        self.top_features_button.grid(row=26, column=1, padx=5, pady=5)

        # Banners
        self.clean_data_banner.grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)
        self.visualizepca_banner.grid(row=14, column=0, columnspan=2, sticky="we", padx=5, pady=5)
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
            self.master.grid_rowconfigure(i, weight=1)

    #### 1. DATA HANDLING METHODS ####

    def load_file(self):
        """Load data from CSV file."""
        try:
            file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
            if file_path:
                self.file_path = file_path  # Save the file path for later use
                self.data = load_file(file_path)
                self.handle_successful_load(file_path)
        except Exception as e:
            self.handle_load_error(e)
            self.handle_load_error(e)

    def run_analysis(self):
        """Execute PCA analysis."""
        if not self.validate_data_exists():
            return

        try:
            # Get analysis parameters
            n_components = int(self.components_entry.get())
            drop_columns = self.get_columns_to_drop()

            # Standardize column names
            self.data.columns = self.data.columns.str.strip().str.lower()
            drop_columns = [col.strip().lower() for col in drop_columns]

            # Filter valid columns to drop
            valid_columns_to_drop = [col for col in drop_columns if col in self.data.columns]
            missing_columns = set(drop_columns) - set(self.data.columns)
            if missing_columns:
                print("Missing columns (not in dataset):", missing_columns)

            # Drop valid columns
            self.data.drop(columns=valid_columns_to_drop, inplace=True)

            # Run analysis using the analyzer
            results = self.pca_analyzer.analyze(
                data=self.data,
                n_components=n_components,
            )

            # Store results
            self.pca_model = results['model']
            self.standardized_data = self.pca_analyzer.standardized_data

            # Update display
            self.update_results_display(results)
            self.toggle_buttons(
                [
                    self.visualize_button,
                    self.biplot_button,
                    self.heatmap_button,
                    self.interactive_biplot_button,
                    self.scree_plot_button,
                    self.save_button,
                ],
                state="normal",
            )
            messagebox.showinfo("Success", "PCA analysis completed successfully!")

        except ValueError as ve:
            messagebox.showerror("Analysis Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"PCA analysis failed: {str(e)}")

    def process_data(self):
        """Process data according to user selections."""
        if not self.validate_data_exists():
            return

        try:
            # Check user-selected columns to drop
            drop_columns = self.get_columns_to_drop()

            # Prepare data using PCAAnalyzer
            prepared_data, missing_cols = self.pca_analyzer.prepare_data(
                self.data,
                drop_columns=drop_columns,
                default_columns_to_drop=DEFAULT_COLUMNS_TO_DROP
            )

            # Log if no columns are dropped
            if not drop_columns and not DEFAULT_COLUMNS_TO_DROP:
                print("No columns were specified for dropping. Proceeding with the original dataset.")

            # Update internal data with prepared data
            self.data = prepared_data
            print(f"Data processed successfully. Shape after preparation: {self.data.shape}")

            # Inform user if any specified columns were missing
            if missing_cols:
                print(f"Warning: The following columns were not found in the dataset: {', '.join(missing_cols)}")
                messagebox.showinfo(
                    "Missing Columns",
                    f"The following columns were not found in the dataset and could not be dropped: {', '.join(missing_cols)}"
                )

        except ValueError as ve:
            # Handle known errors gracefully
            print(f"ValueError during data preparation: {str(ve)}")
            messagebox.showerror("Data Preparation Error", str(ve))

        except Exception as e:
            # Handle unexpected errors with a user-friendly message
            print(f"Unexpected error during data preparation: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred during data preparation: {str(e)}")

    def select_output_directory(self):
        """Allow the user to select an output directory for saving plots."""
        selected_dir = filedialog.askdirectory()
        if selected_dir:  # If the user selects a directory
            self.output_dir = selected_dir
            self.output_dir_label.config(text=f"Output Directory: {self.output_dir}")
            messagebox.showinfo("Directory Selected", f"Output directory set to:\n{self.output_dir}")
        else:
            messagebox.showwarning("No Directory Selected", "Using the default output directory.")

    def clean_data(self):
        """Clean the data and prepare it for PCA analysis."""
        if not hasattr(self, 'file_path') or not self.file_path:
            messagebox.showerror("Error", "No file loaded. Please load a CSV file first.")
            return

        try:
            # Detect file encoding and load the data
            with open(self.file_path, 'rb') as file:
                result = chardet.detect(file.read())
            encoding = result['encoding']
            self.data = pd.read_csv(self.file_path, encoding=encoding)
            self.data.replace([np.inf, -np.inf], np.nan, inplace=True)

            # Convert int64 to float for PCA compatibility
            for col in self.data.columns:
                if self.data[col].dtype == 'int64':
                    self.data[col] = self.data[col].astype(float)

            # Ensure BBCH column exists and is treated as string
            if 'bbch' in self.data.columns:
                self.data['bbch'] = self.data['bbch'].astype(str).str.strip()

            # Filter by BBCH stage
            selected_bbch = self.bbch_choice.get()
            if selected_bbch == 59:
                self.data = self.data[self.data['bbch'] == 'B59']
            elif selected_bbch == 69:
                self.data = self.data[self.data['bbch'] == 'B69']
            elif selected_bbch == 85:
                self.data = self.data[self.data['bbch'] == 'B85']
            elif selected_bbch == -1:
                pass  # No filter applied if selected is -1 (all stages)

            # Drop user-specified columns
            drop_columns = self.get_columns_to_drop()
            self.data.columns = self.data.columns.str.strip().str.lower()  # Standardize column names
            drop_columns = [col.strip().lower() for col in drop_columns]  # Ensure consistency

            # Filter valid columns to drop
            valid_columns_to_drop = [col for col in drop_columns if col in self.data.columns]
            missing_columns = set(drop_columns) - set(self.data.columns)
            if missing_columns:
                print(
                    f"Warning: The following columns were not found in the dataset and could not be dropped: {missing_columns}")
            self.data.drop(columns=valid_columns_to_drop, inplace=True, errors='ignore')

            # Drop non-numeric columns except BBCH
            if 'bbch' in self.data.columns:
                non_numeric_cols = self.data.select_dtypes(exclude=[float, int]).columns
                non_numeric_cols = non_numeric_cols.drop('bbch', errors='ignore')
                self.data.drop(columns=non_numeric_cols, inplace=True, errors='ignore')

            # Handle missing values
            if self.missing_choice.get() == "impute_mean":
                imputer = SimpleImputer(strategy='mean')
            elif self.missing_choice.get() == "impute_median":
                imputer = SimpleImputer(strategy='median')
            elif self.missing_choice.get() == "replace_nan":
                imputer = SimpleImputer(strategy='constant', fill_value=0)
            elif self.missing_choice.get() == "leave_empty":
                imputer = SimpleImputer(strategy='constant', fill_value=np.nan)
            else:
                messagebox.showerror("Error", "Please select a valid missing value handling strategy.")
                return

            # Impute missing values
            if self.data.isnull().any().any():
                x_imputed = imputer.fit_transform(self.data)
                self.data = pd.DataFrame(x_imputed, columns=self.data.columns)

            # Enable buttons and update UI
            self.run_button.config(state="normal")
            self.visualize_button.config(state="normal")
            self.heatmap_button.config(state="normal")  # Enable heatmap button after cleaning
            self.update_data_info()
            self.is_cleaned = True
            messagebox.showinfo("Data Cleaned", "Data cleaned successfully and ready for PCA.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during data cleaning: {e}")

    def is_clean_data(self):
        """Check if the loaded data meets the criteria for cleaned data."""
        if self.data.isnull().values.any():
            print("Data contains missing values.")  # Debug
            return False

        if not all(pd.api.types.is_numeric_dtype(self.data[col]) for col in self.data.columns):
            print("Non-numeric columns detected.")  # Debug
            return False

        return True

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

    def visualize_pca(self):
        """Create PCA visualization."""
        try:
            if not hasattr(self, 'pca_model') or self.pca_model is None:
                raise ValueError("Please run PCA analysis first.")

            # Reset the canvas
            self.reset_canvas()

            # Get the target variable
            target_variable = self.get_target_variable()
            if target_variable and target_variable not in self.data.columns:
                raise ValueError(f"Target variable '{target_variable}' not found in the dataset.")

            # Debugging (optional)
            print("Target variable:", target_variable)
            print("Data columns:", self.data.columns.tolist())

            # Perform PCA transformation
            pca_visualizer = PCAVisualizer(self.fig, self.ax)
            transformed_data = self.pca_model.transform(self.standardized_data)

            # Plot the PCA visualization, grouped by target
            pca_visualizer.plot(
                principal_components=transformed_data,
                data=self.data,
                target=target_variable,
                target_mode=self.target_mode.get().strip().lower()
            )

            # Redraw the canvas
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))

    def create_scree_plot(self):
        """Create scree plot."""
        try:
            if not hasattr(self, 'pca_model') or self.pca_model is None:
                raise ValueError("Please run PCA analysis first")

            # Reset the canvas
            self.reset_canvas()

            scree_visualizer = ScreePlotVisualizer(self.fig, self.ax)
            scree_visualizer.create_scree_plot(self.pca_model)

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            messagebox.showerror("Error", f"Error creating scree plot: {str(e)}")

    def create_biplot(self):
        """Create biplot visualization."""
        try:
            if not hasattr(self, 'pca_model') or self.pca_model is None:
                raise ValueError("Please run PCA analysis first.")

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
                text_distance = float(self.text_distance_entry.get())
            except ValueError:
                text_distance = 1.1  # Default to 1.1 if invalid input

            # Delegate to BiplotVisualizer
            biplot_visualizer = BiplotVisualizer(self.fig, self.ax)
            biplot_visualizer.create_biplot(
                pca_model=self.pca_model,
                x_standardized=self.standardized_data,
                data=self.data,
                feature_to_group=self.feature_to_group,
                enable_feature_grouping=self.enable_feature_grouping.get(),
                top_n=top_n,
                text_distance=text_distance,
                focus_on_loadings=self.focus_on_loadings.get()
            )

            # Apply clarity improvements
            self.ax.grid(True, linestyle='--', alpha=0.3)
            self.ax.set_facecolor('#f8f9fa')
            self.ax.set_aspect('equal', adjustable='box')

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            messagebox.showerror("Error", f"Error creating biplot: {str(e)}")

    def create_interactive_biplot(self):
        """Create an interactive biplot visualization."""
        try:
            if not hasattr(self, 'pca_model') or self.pca_model is None:
                raise ValueError("Please run PCA analysis first")

            interactive_visualizer = InteractiveBiplotVisualizer()
            fig = interactive_visualizer.create_interactive_biplot(
                pca_model=self.pca_model,
                x_standardized=self.standardized_data,
                data=self.data,
                top_n_entry=self.components_entry,  # Replace with actual entry for top N
                text_distance_entry=self.components_entry,  # Replace with actual entry for text distance
                enable_feature_grouping=self.enable_feature_grouping.get(),
                feature_to_group=self.feature_to_group,
            )

            save_path = interactive_visualizer.save_interactive_biplot(fig, OUTPUT_DIR)
            messagebox.showinfo("Success", f"Interactive biplot saved at {save_path}")


        except Exception as e:
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")

    def plot_loadings_heatmap(self):
        """Plot loadings heatmap using user-selected mode."""
        try:
            if not hasattr(self, 'pca_model') or self.pca_model is None:
                raise ValueError("PCA analysis has not been performed yet.")

            # Reset the canvas
            self.reset_canvas()

            # Retrieve heatmap mode (e.g., from a dropdown)
            heatmap_mode = self.heatmap_mode_var.get()  # Ensure the actual value is retrieved
            if not heatmap_mode:
                raise ValueError("Heatmap mode is not defined.")

            # Calculate PCA loadings
            loadings = self.pca_model.components_.T

            # Determine focus columns
            focus_columns = self.get_focus_columns(heatmap_mode, focus_entry=self.focus_entry.get())

            # Create and display heatmap
            heatmap_visualizer = LoadingsHeatmapVisualizer(self.fig, self.ax)
            heatmap_visualizer.display_loadings_heatmap(
                loadings=loadings,
                data_columns=self.data.columns.tolist(),
                focus_columns=focus_columns,
                cmap="coolwarm"
            )

            self.canvas.draw()  # This ensures the new plot appears on the canvas

        except Exception as e:
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def plot_top_features_loadings(self):
        """Plot top feature loadings using LoadingsProcessor."""

        # Reset the canvas
        self.reset_canvas()

        if not hasattr(self, 'pca_model') or self.pca_model is None:
            messagebox.showerror("Error", "PCA analysis has not been performed yet.")
            return

        try:
            # Initialize LoadingsProcessor
            loadings_processor = LoadingsProcessor(self.pca_model, self.data)

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
            messagebox.showerror("Error", f"Failed to plot top feature loadings: {str(e)}")

    #### 3. UTILITY METHODS ####

    def get_columns_to_drop(self) -> list:
        """Get list of columns to drop from user input."""
        return [col.strip() for col in self.drop_entry.get().split(",") if col.strip()]

    def replace_column_name(self):
        """Replace a column name in the loaded dataset."""
        if not self.validate_data_exists():
            return

        try:
            # Get the old and new column names from the input fields
            old_name = self.replace_old_entry.get().strip()
            new_name = self.replace_new_entry.get().strip()

            # Ensure the column exists in the dataset
            if old_name not in self.data.columns:
                messagebox.showerror("Error", f"Column '{old_name}' not found in the dataset.")
                return

            # Ensure the new name is not empty
            if not new_name:
                messagebox.showerror("Error", "New column name cannot be empty.")
                return

            # Replace the column name
            self.data.rename(columns={old_name: new_name}, inplace=True)

            # Update the dataset info displayed in the GUI
            self.update_data_info()

            messagebox.showinfo("Success", f"Column '{old_name}' successfully renamed to '{new_name}'.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to replace column name: {str(e)}")

    def get_target_variable(self) -> str:
        """Get selected target variable."""
        target_mode = self.target_mode.get().strip().lower()
        if target_mode == "bbch":
            return "bbch"
        elif target_mode == "input specific target":
            return self.custom_target_entry.get().strip().lower()
        return None

    def validate_data_exists(self) -> bool:
        """Check if data is loaded."""
        if not hasattr(self, 'data') or self.data is None:
            messagebox.showerror("Error", "No data loaded. Please load a CSV file first.")
            return False
        return True

    def update_figure(self):
        """Update the matplotlib figure."""
        self.canvas.draw()

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
            print("Mapping file loaded successfully.")
            print(self.biplot_manager.feature_to_group)
            print(self.biplot_manager.group_colors)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")

    def get_focus_columns(self, heatmap_mode_var, focus_entry=None):
        """Determine columns to focus on based on heatmap mode."""
        try:
            if heatmap_mode_var == "Top 10 Features":
                return self.data.columns[:10].tolist()  # Top 10 features by default
            elif heatmap_mode_var == "Top 20 Features":
                return self.data.columns[:20].tolist()  # Top 20 features by default
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

    def update_focus_on_loadings(self):
        """
        Update logic or perform actions based on the checkbox state.
        """
        focus_value = self.focus_on_loadings.get()  # Retrieve the value (True/False)

    #### 4. UI UPDATE METHODS ####

    def update_data_info(self):
        """Update display with simplified data information."""
        if self.validate_data_exists():
            # Simple, clean formatting
            info_text = "Data Information\n"
            info_text += "═══════════════\n\n"
            info_text += f"Dataset Shape: {self.data.shape[0]} rows × {self.data.shape[1]} columns\n\n"
            info_text += "Columns:\n"

            # Simple column listing
            columns = self.data.columns.tolist()
            for i, col in enumerate(columns, 1):
                info_text += f"{i}. {col}\n"

            # Update the results summary box
            self.pcaresults_summary.delete(1.0, tk.END)
            self.pcaresults_summary.insert(tk.END, info_text)

    def update_results_display(self, results: dict):
        """Update results display with simplified formatting."""
        self.pcaresults_summary.delete(1.0, tk.END)

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

        self.pcaresults_summary.insert(tk.END, summary)

    def enable_visualization_buttons(self):
        """Enable visualization buttons."""
        for button in [self.visualize_button, self.biplot_button,
                       self.interactive_biplot_button, self.heatmap_button,
                       self.scree_plot_button, self.save_button]:
            button.config(state="normal")

    def disable_visualization_buttons(self):
        """Disable visualization buttons."""
        for button in [self.visualize_button, self.biplot_button,
                       self.interactive_biplot_button, self.heatmap_button,
                       self.scree_plot_button, self.save_button]:
            button.config(state="disabled")

    def toggle_buttons(self, buttons, state="normal"):
        for button in buttons:
            button.config(state=state)

    def toggle_feature_grouping(self):
        """Toggle the feature grouping functionality."""
        if self.enable_feature_grouping.get():
            # Enable the mapping upload button
            self.mapping_button.config(state="normal")
            messagebox.showinfo("Feature Grouping Enabled",
                                "Feature grouping is now enabled. Please upload a mapping file.")
        else:
            # Disable the mapping upload button and reset group-related variables
            self.mapping_button.config(state="disabled")
            self.feature_to_group = None
            self.feature_groups_colors = None

            # Re-enable dependent buttons if PCA is complete
            if hasattr(self, 'pca_model') and self.pca_model is not None:
                self.biplot_button.config(state="normal")
                self.interactive_biplot_button.config(state="normal")

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

                # Debugging: Print updated colors
                print(f"Debug: Updated feature group colors for palette '{selected_palette}':")
                print(self.feature_groups_colors)
            else:
                messagebox.showinfo("No Groups Defined", "No feature groups are currently defined.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update color palette: {str(e)}")


    def update_target_input(self, *args):
        """Enable or disable the target input box based on the dropdown selection."""
        if self.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.delete(0, tk.END)
            self.custom_target_entry.config(state="disabled")

    #### 5. EVENT HANDLERS ####

    def handle_successful_load(self, file_path: str):
        """Handle successful file load."""
        messagebox.showinfo("Success", f"File loaded successfully: {file_path}")
        self.update_data_info()
        self.run_button.config(state="normal")

    def handle_load_error(self, error: Exception):
        """Handle file loading errors."""
        messagebox.showerror("Error", f"Failed to load file: {str(error)}")

    def save_plot(self):
        """Save the current plot using the dynamic output directory."""
        try:
            save_path = save_plot(self.fig, output_dir=self.output_dir)
            messagebox.showinfo("Success", f"Plot saved at:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save plot: {str(e)}")















































