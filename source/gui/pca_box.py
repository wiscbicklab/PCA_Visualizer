import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import pandas as pd

from sklearn.impute import SimpleImputer

from source.visualization.pca_visualization import PCAVisualizer


from source.utils.constant import *


class PcaBox(tk.Frame):
    """
    Creates a space for PCA options
    """

    def __init__(self, main=None, df=None, **kwargs):
        super().__init__(main, **kwargs)

        # Variables
        self.target_mode = None

        self.init_vars()

        # Visualization button
        self.visualize_button = None

        # Banner
        self.visualizepca_banner = None

        # Select Target Variable Section
        self.target_label = None
        self.target_dropdown = None
        self.custom_target_entry = None

        # Data validation handler
        self.vcmd_pi = None

        # PCA Parameters Section
        self.components_label = None
        self.components_entry = None

        # Top N Feature User Input
        self.top_n_label = None
        self.top_n_entry = None

        # Text Distance for Labels User Input
        self.text_distance_label = None
        self.text_distance_entry = None

        self.create_components()
        self.setup_layout()

    def init_vars(self):
        self.target_mode = tk.StringVar()
        self.target_mode.set("None")  # Default option

    def create_components(self):
        # Visualization button
        self.visualize_button = tk.Button(self,
                                          text="Visualize PCA",
                                          **BUTTON_STYLE,
                                          command=self.visualize_pca)
        
        # Banner
        self.visualizepca_banner = tk.Label(self,
                                            text="Visualize PCA",
                                            font=("Helvetica", 12),
                                            bg="#dcdcdc",
                                            relief="groove")
        
        # Input box for custom target
        # Dropdown for selecting predefined targets
        self.target_label = tk.Label(self, text="Target Variable:", **LABEL_STYLE)
        target_options = ["None", "bbch", "Input Specific Target"]
        self.target_dropdown = tk.OptionMenu(self, self.target_mode, *target_options)
        self.target_dropdown.config(font=LABEL_STYLE["font"], bg="#007ACC", fg="white",
                                    activebackground="#005f99", relief="flat")
        self.custom_target_entry = tk.Entry(self, **LABEL_STYLE, width=20, state="disabled")

        # Create data validation handlers
        self.vcmd_pi = (self.register(self.validate_positive_integer), '%P')

        # PCA Parameters Section
        self.components_label = tk.Label(self,
                                         text="Number of PCA Components:",
                                         **LABEL_STYLE)
        self.components_entry = tk.Entry(self,
                                         font=LABEL_STYLE["font"],
                                         width=10,
                                         validate="key",
                                         validatecommand=self.vcmd_pi)
        self.components_entry.insert(0, "2")

        # Bind focus out event to reset empty input
        self.components_entry.bind("<FocusOut>", self.on_focus_out)

        # Top N Feature User Input
        self.top_n_label = tk.Label(self, text="Top N Features for Biplot:", bg=LABEL_STYLE["bg"], font=LABEL_STYLE["font"])
        self.top_n_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=10)
        self.top_n_entry.insert(0, "10")  # Default to 10

        # Test Distance for Lables User Input
        self.text_distance_label = tk.Label(self, text="Text Distance for Labels:", bg=LABEL_STYLE["bg"],
                                            font=LABEL_STYLE["font"])
        self.text_distance_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=10)
        self.text_distance_entry.insert(0, "1.1")  # Default to 1.1

    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # PCA Parameters
        self.visualizepca_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)
    
        # Target Selection Section
        self.target_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.target_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.custom_target_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.components_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.components_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.top_n_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.top_n_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.text_distance_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.text_distance_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Run Analysis Buttons
        self.visualize_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)



    #### 5. EVENT HANDLERS ####

    def validate_positive_integer(self, proposed_value):
        if proposed_value.isdigit() and int(proposed_value) > 0:
            self.df_updated = True
            return True
        elif proposed_value == "":
            return True  # Allow clearing before retyping
        return False
    
    def on_focus_out(self, event):
        value = self.components_entry.get()
        if value.strip() == "":
            self.components_entry.delete(0, tk.END)
            self.components_entry.insert(0, "2")



    #### 6. Data Handling ####

    def visualize_pca(self):
        """Create PCA visualization."""
        if not self.df_clean:
            return
        
        try:
            # Ensures PCA has been run
            self.run_analysis()

            # Reset the canvas
            self.reset_canvas()

            # Get the target variable
            target_variable = self.get_target_variable()
            if target_variable and target_variable not in self.df.columns:
                raise ValueError(f"Target variable '{target_variable}' not found in the dataset.")

            # Perform PCA transformation
            pca_visualizer = PCAVisualizer(self.fig, self.ax)
            transformed_data = self.pca_results['transformed_data']

            # Plot the PCA visualization, grouped by target
            pca_visualizer.plot(
                principal_components=transformed_data,
                data=self.df,
                target=target_variable,
                target_mode=self.target_mode.get().strip().lower()
            )

            # Redraw the canvas
            self.canvas.draw()
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Visualization Error", str(e))
    
    



