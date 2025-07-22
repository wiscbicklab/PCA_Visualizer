import tkinter as tk
from tkinter import messagebox
import traceback
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


from .app_state import AppState
from source.utils.constant import *


class HeatmapBox(tk.Frame):
    """
    A GUI box for generating a Heatmap

    A banner with a header for the section
    A label and dropdown menu for the number of features to focus on
    A label and entry box for entering custom features to focus on
    A button for creating and showing the heatmap

    """

    def __init__(self, main, app_state: AppState, **kwargs):
        """
        Creats a space for Biplot generation buttons

        Args:
            main: tk.Widget
                The parent widget for this frame.
            app_state: AppState
                The app_state variable used to pass data between components
            **kwargs: dict
                Additional keyword arguments passed to tk.Frame.
        """
        super().__init__(main, **kwargs)
        self.app_state = app_state

        self.heatmap_mode_var = tk.StringVar(value="Top Features")

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
        """Creates the components to be placed onto this tk Frame"""
        # Banner
        self.heatmap_banner = tk.Label(self, **BANNER_STYLE, text="Heatmap Generation")
        

        # Heatmap Controls
        heatmap_options = ["Top Features", "Custom Features"]
        self.heatmap_mode_label = tk.Label(self, text="Select Heatmap Mode:", **LABEL_STYLE)
        self.heatmap_mode_menu = tk.OptionMenu( self, self.heatmap_mode_var, *heatmap_options)
        self.heatmap_mode_var.trace_add("write", self.toggle_custom_heatmap_entry)

        self.focus_label = tk.Label(self, text="Columns to Focus On (comma-separated):", **LABEL_STYLE)
        self.focus_entry = tk.Entry(self, **BIG_ENTRY_STYLE)
        self.focus_entry.configure(state="disabled")

        self.heatmap_button = tk.Button(self, text="Plot Heatmap", command=self.create_heatmap_fig, **BUTTON_STYLE)

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)


        # Banners
        self.heatmap_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Heatmap Section
        self.heatmap_mode_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.heatmap_mode_menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.focus_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.focus_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.heatmap_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5)


    #### 2. VISUALIZATION METHODS ####

    def create_heatmap_fig(self):
        """
        Plot loadings heatmap using user-selected mode.
        
        Creates a heatmap using the top number of features selected or custom features.
            Shows the number of PCA components selected, and sorts the features by absolute 
            loadings of the selected PCA component to analize
        """
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Creates a new blank figure
            self.app_state.main.create_blank_fig(grid=False)

            # Adds a title and x and y label 
            self.app_state.axes.set_title('Loadings Heatmap', fontsize=16)
            self.app_state.axes.set_xlabel('Principal Components', fontsize=14)
            self.app_state.axes.set_ylabel('Features', fontsize=14)

            # Sets tick parameters to fit on ax
            self.app_state.axes.tick_params(axis='x', labelsize=12)
            self.app_state.axes.tick_params(axis='y', labelsize=10)

            # Get user entered heatmap mode and PCA data
            heatmap_mode = self.heatmap_mode_var.get()
            loadings = abs(self.app_state.pca_results['loadings'])

            # Determine focus columns
            focus_columns = self.get_focus_cols(loadings, focus_entry=self.focus_entry.get())

            # Update the heatmap figure
            self.display_loadings_heatmap(
                loadings=loadings,
                data_columns=self.app_state.df.columns.tolist(),
                focus_columns=focus_columns,
                cmap="coolwarm"
            )

            # Ensure that the GUI updates
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def get_focus_cols(self, loadings, focus_entry=None):
        """Determine columns to focus on based on heatmap mode."""
        try:
            # Get the column and loadings data
            df_cols = self.app_state.df.columns.tolist()

            # Get absolute loadings for the first principal component
            pc1_loadings = abs(loadings[:, self.app_state.focused_pca_num.get()-1])
            loading_series = pd.Series(pc1_loadings, index=df_cols)
            sorted_columns = loading_series.sort_values(ascending=False).index.tolist()

            heatmap_mode = self.heatmap_mode_var.get()

            if heatmap_mode == "Top Features":
                return sorted_columns[:self.app_state.num_feat.get()]  # Uses the user specified number of Features
            elif heatmap_mode == "Custom Features":
                if focus_entry:
                    cols = [col.strip() for col in focus_entry.split(",") if col.strip()]
                    if not cols:
                        raise ValueError("No valid columns specified for custom heatmap.")
                    # Check if specified columns exist
                    missing_columns = [col for col in cols if col not in df_cols]
                    if missing_columns:
                        raise ValueError(f"The following columns are not in the dataset: {', '.join(missing_columns)}")
                    return cols
                else:
                    raise ValueError("No columns specified for custom heatmap.")
            else:
                raise ValueError(f"Invalid heatmap mode: {heatmap_mode}")

        except Exception as e:
            messagebox.showerror("Error", f"Error determining focus columns: {str(e)}")
            return None

    def display_loadings_heatmap(self, loadings, data_columns, focus_columns=None, cmap='viridis'):
        """
        Display a heatmap of loadings with improved design.

        Args:
            loadings: PCA loadings matrix.
            data_columns: List of all data column names.
            focus_columns: List of columns to focus on. Defaults to None.
            cmap: Colormap to use for the heatmap.
        """
        if focus_columns is None:
            focus_columns = data_columns  # Default to all columns if none specified

        # Select only the relevant rows from the loadings matrix
        selected_loadings = loadings[[data_columns.index(col) for col in focus_columns], :]

        # Create the heatmap
        plt.figure(self.app_state.fig_size[0])  # Increase figure size for clarity
        sns.heatmap(
            selected_loadings,
            annot=True,  # Add annotations to cells
            fmt=".2f",  # Format numbers
            cmap=cmap,  # Use perceptually uniform colormap
            cbar_kws={'label': 'Absolute Loadings'},  # Single, descriptive colorbar
            xticklabels=[f'PC{i + 1}' for i in range(loadings.shape[1])],
            yticklabels=focus_columns,
            ax=self.app_state.axes
        )

        # Adds a title and x and y label
        self.app_state.axes.set_title('Loadings Heatmap', fontsize=16)
        self.app_state.axes.set_xlabel('Principal Components', fontsize=14)
        self.app_state.axes.set_ylabel('Features', fontsize=14)
        # Sets axis lablel size
        self.app_state.axes.tick_params(axis='x', labelsize=12)
        self.app_state.axes.tick_params(axis='y', labelsize=10)

    #### 3. EVENT HANDLERS ####

    def toggle_custom_heatmap_entry(self, *args):
        """Toggles the custom_heatmap_entry to accept or refuse input"""
        if self.heatmap_mode_var.get() == "Custom Features":
            self.focus_entry.configure(state="normal")
        else:
            self.focus_entry.delete(0, tk.END)
            self.focus_entry.configure(state="disabled")


