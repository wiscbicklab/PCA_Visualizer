import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import pandas as pd
import numpy as np
import os, time

from sklearn.impute import SimpleImputer

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from source.visualization.pca_visualization import PCAVisualizer
from source.visualization.biplot import BiplotVisualizer, InteractiveBiplotVisualizer, BiplotManager
from source.visualization.loadings import LoadingsProcessor

from source.utils.constant import *

import source.utils.file_operations as file_ops


class BiplotBox(tk.Frame):
    """
    Creats a space for Biplot generation buttons
    """

    def __init__(self, main, fig, **kwargs):
        super().__init__(main, **kwargs)

        self.main = main
        self.fig = fig
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=main)
        self.canvas_widget = self.canvas.get_tk_widget()

        # Sets up visualization dependencies
        self.biplot_visualizer = BiplotVisualizer()
        self.biplot_manager = BiplotManager()

        # Variables
        self.enable_feature_grouping = None

        self.init_variables()

        #TODO This will need to be updated
        # Feature Results
        self.feature_results_summary = None

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

    def init_variables(self):
        self.enable_feature_grouping = tk.BooleanVar(value=False)

    def create_components(self):
        # Banner
        self.biplot_banner = tk.Label(self,
                                      text="Biplot Section",
                                      font=("Helvetica", 12),
                                      bg="#dcdcdc",
                                      relief="groove")
        
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

    def setup_layout(self):
        # Banners
        self.biplot_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Feature Grouping
        self.grouping_checkbox.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.mapping_label.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.mapping_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Visualization Buttons
        self.scree_plot_button.grid(row=3, column=0, padx=5, pady=5)
        self.biplot_button.grid(row=3, column=1, padx=5, pady=5)
        self.interactive_biplot_button.grid(row=4, column=0, padx=5, pady=5)
        self.top_features_button.grid(row=4, column=1, padx=5, pady=5)


    #### 2. VISUALIZATION METHODS ####

    def reset_plot(self):
        """Clear the canvas and reinitialize the figure and axes"""
        # Clear the entire figure
        self.fig.clear()

        # Create a fresh subplot
        self.ax = self.fig.add_subplot(111)

        # Update the canvas to use the cleared figure
        self.canvas.figure = self.fig
        self.canvas.draw()

    def create_scree_plot(self, pca_model):
        """Create scree plot."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.main.run_analysis()

            # Reset the canvas
            self.reset_plot()

            # Create scree plot - exact match to original
            explained_variance = pca_model.explained_variance_ratio_

            # Bar plot of individual explained variance
            self.ax.bar(
                range(1, len(explained_variance) + 1),
                explained_variance,
                alpha=0.7,
                align='center'
            )

            # Step plot of cumulative explained variance
            self.ax.step(
                range(1, len(explained_variance) + 1),
                np.cumsum(explained_variance),
                where='mid',
                label='Cumulative explained variance'
            )

            # Labels and title - exact match
            self.ax.set_xlabel('Principal Component Index')
            self.ax.set_ylabel('Explained Variance Ratio')
            self.ax.set_title('Scree Plot')

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
            self.main.run_analysis()

            # Reset the canvas before plotting
            self.reset_plot()

            # Validate and retrieve user inputs
            top_n = int(self.top_n_entry.get())
            text_dist = float(self.text_distance_entry.get())


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

    def plot_top_features_loadings(self):
        """Plot top feature loadings using LoadingsProcessor."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Reset the canvas
            self.reset_plot()

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

