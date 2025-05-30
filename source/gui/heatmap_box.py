import tkinter as tk
from tkinter import messagebox
import traceback
from matplotlib.figure import Figure
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


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
        """Creates the components to be placed onto this tk Frame"""
        # Banner
        self.heatmap_banner = tk.Label(self, **BANNER_STYLE, text="Heatmap Section")
        

        # Heatmap Controls
        heatmap_options = ["Top 10 Features", "Top 20 Features", "Custom Features"]
        self.heatmap_mode_label = tk.Label(self, text="Select Heatmap Mode:", **LABEL_STYLE)
        self.heatmap_mode_menu = tk.OptionMenu( self, self.heatmap_mode_var, *heatmap_options)

        self.focus_label = tk.Label(self, text="Columns to Focus On (comma-separated):", **LABEL_STYLE)
        self.focus_entry = tk.Entry(self, **ENTRY_STYLE)

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
        """Plot loadings heatmap using user-selected mode."""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return
        
        try:
            heatmap_mode = self.heatmap_mode_var.get()
            if heatmap_mode == "Top 10 Features":
                self.app_state.top_n_feat.set(10)
            else:
                self.app_state.top_n_feat.set(20)

            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Reset the canvas
            if not self.init_fig():
                messagebox.showerror("Error", f"Failed to plot top feature loadings: {str(e)}")

            pca_comp_num = self.app_state.pca_num.get()-1
            top_n = self.app_state.num_pca_comp.get()


            # Validate and retrieve loadings
            loadings = abs(self.app_state.pca_results['components'])
            feat_names = self.app_state.pca_results['feature_names']

            # Sorting the loadings
            sorted_pairs = sorted(zip(feat_names, loadings), key=lambda x: abs(x[1][pca_comp_num]), reverse=True)

            sorted_feat_names, sorted_loadings = zip(*sorted_pairs)
            sorted_loadings_rows = list(sorted_loadings)
            sorted_feat_names = list(sorted_feat_names)

            # Convert list of vectors back into a 2D array
            sorted_loadings_array = np.vstack(sorted_loadings_rows)
            sorted_loadings_rows = sorted_loadings_rows[:, :top_n]

            # Retrieve heatmap mode (e.g., from a dropdown)

            # Determine focus columns
            #focus_columns = self.get_focus_columns(heatmap_mode, focus_entry=self.focus_entry.get())

            # Create and display heatmap
            self.display_loadings_heatmap(
                loadings=sorted_loadings_array,
                feat_names=sorted_feat_names,
                cmap="coolwarm"
            )

            self.app_state.main.update_figure()  # This ensures the new plot appears on the canvas

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def init_fig(self):
        """Clear the canvas and reinitialize the figure and axes."""
        try:
            self.app_state.fig = Figure(self.app_state.fig_size)
            self.app_state.ax = self.app_state.fig.add_subplot(111)

            self.app_state.ax.set_title('Loadings Heatmap', fontsize=16)
            self.app_state.ax.tick_params(axis='x', labelsize=12)
            self.app_state.ax.tick_params(axis='y', labelsize=10)
            self.app_state.ax.set_xlabel('Principal Components', fontsize=14)
            self.app_state.ax.set_ylabel('Features', fontsize=14)
            
            return True
        except Exception:
            return False


    def display_loadings_heatmap(self, loadings, feat_names, cmap='viridis'):
        """
        Display a heatmap of loadings with improved design.
        :param loadings: PCA loadings matrix
        :param data_columns: List of all data column names
        :param focus_columns: List of columns to focus on (optional)
        :param cmap: Colormap for heatmap
        """

        # Create the heatmap
        plt.figure(figsize=(10, 12))  # Increase figure size for clarity
        sns.heatmap(
            loadings,
            annot=True,  # Add annotations to cells
            fmt=".2f",  # Format numbers
            cmap=cmap,  # Use perceptually uniform colormap
            cbar_kws={'label': 'Absolute Loadings'},  # Single, descriptive colorbar
            xticklabels=[f'PC{i + 1}' for i in range(loadings.shape[1])],
            yticklabels=feat_names,
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
                    missing_columns = [col for col in columns if col not in self.app_state.df.columns]
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




    def validate_and_get_loadings(self, heatmap_mode, focus_entry=None):
        """
        Validates PCA model and retrieves loadings based on mode.

        Args:
            heatmap_mode (str): Mode to determine which features to focus on.
            focus_entry (str): Comma-separated column names for custom focus (optional).

        Returns:
            Tuple[np.ndarray, List[str]]: Loadings array and list of focus columns.
        """
        try:
            # Extract loadings
            loadings = self.app_state.pca_results["loadings"]
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