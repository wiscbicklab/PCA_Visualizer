import tkinter as tk
from tkinter import messagebox
import traceback

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from source.visualization.pca_visualization import PCAVisualizer


from source.utils.constant import *


class PcaBox(tk.Frame):
    """
    Creates a space for PCA options
    """

    def __init__(self, main: tk.TK, **kwargs):
        super().__init__(main, **kwargs)
        self.main = main

        # Sets the PCA analysis Target
        self.target_mode = tk.StringVar()
        self.target_mode.set("None")  # Default option

        # Banner
        self.banner = None

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

        # Visualization button
        self.button = None

        self.create_components()
        self.setup_layout()


    def create_components(self):
        # Visualization button
        self.button = tk.Button(self, text="Visualize PCA", **BUTTON_STYLE, 
                                command=self.visualize_pca)
                                
        # Banner
        self.banner = tk.Label(self, text="Visualize PCA", font=("Helvetica", 12),
                               bg="#dcdcdc", relief="groove")
        
        # Input box for custom target
        # Dropdown for selecting predefined targets
        self.target_label = tk.Label(self, text="Target Variable:", **LABEL_STYLE)
        target_options = ["None", "bbch", "Input Specific Target"]
        self.target_dropdown = tk.OptionMenu(self, self.target_mode, *target_options)
        self.target_dropdown.config(font=LABEL_STYLE["font"], bg="#007ACC", fg="white",
                                    activebackground="#005f99", relief="flat")
        self.custom_target_entry = tk.Entry(self, **LABEL_STYLE, width=20, state="disabled")

        # Validate Posititive Integer Command
        self.vcmd_pi = (self.register(self.validate_positive_integer), '%P')

        # PCA Parameters Section
        self.components_label = tk.Label(self, text="Number of PCA Components:", **LABEL_STYLE)
        self.components_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=10,
                                         validate="key", validatecommand=self.vcmd_pi)
        self.components_entry.insert(0, "2")

        # Bind focus out event to reset empty input
        self.components_entry.bind("<FocusOut>", self.on_focus_out)

        # Top N Feature User Input
        self.top_n_label = tk.Label(self, text="Top N Features for Biplot:", **LABEL_STYLE)
        self.top_n_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=10)
        self.top_n_entry.insert(0, "10")  # Default to 10

        # Test Distance for Lables User Input
        self.text_distance_label = tk.Label(self, text="Text Distance for Labels:", **LABEL_STYLE)
        self.text_distance_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=10,
                                            validate="key", validatecommand=self.vcmd_pi)
        self.text_distance_entry.insert(0, "1.1")  # Default to 1.1

    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # PCA Parameters
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)
    
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
        self.button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)



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
        if not self.main.df_clean:
            return
        
        try:
            # Get the target variable and raise error if it's not in the data set

            # Get analysis parameters
            n_components = int(self.components_entry.get())

            # Run PCA and get the transformed data
            self.main.run_analysis(n_components)
            transformed_data = self.main.pca_results['transformed_data']

            # Convert principal_components to DataFrame
            principal_df = pd.DataFrame(
                transformed_data,
                columns=[f'PC{i + 1}' for i in range(transformed_data.shape[1])],
            )

            # Plot the PCA visualization, grouped by target
            self.plot(principal_df)

            # Redraw the Tkinter window, Updating the GUI
            self.main.canvas.draw()
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Visualization Error", str(e))
    
    def plot(self, principal_df: pd.DataFrame):
        """
        Visualize PCA results.
        """
        # Creats a new figure and ax
        self.main.fig = Figure(figsize=(5, 5))
        self.main.ax = self.main.fig.add_subplot(111)

        # Set labels and grid
        self.main.ax.set_xlabel("Principal Component 1")
        self.main.ax.set_ylabel("Principal Component 2")
        self.main.ax.set_title("PCA Visualization")
        self.main.ax.grid(True)

        # Gets the target mode
        target_mode=self.target_mode.get().strip().lower()
        if target_mode not in self.main.df.columns and target_mode != "":
                raise ValueError(f"Target variable '{target_mode}' not found in the dataset.")
        
        # Determines target
        if target_mode == "bbch":
            target = "bbch"
        elif target_mode == "input specific target":
            if not target:
                raise ValueError("Please enter a target variable.")
        else:
            target = None

        # Plots the data onto the ax
        try:
            # Plot grouped by target if available
            if target and target in self.main.df.columns:
                target_vals = self.main.df[target]
                unique_targets = sorted(target_vals.unique())

                # Assign colors dynamically
                colors = plt.cm.tab10(np.linspace(0, 1, len(unique_targets)))
                for i, t in enumerate(unique_targets):
                    mask = target_vals == t
                    color = colors[i] 
                    self.main.ax.scatter(principal_df.loc[mask, "PC1"],
                                         principal_df.loc[mask, "PC2"],
                                         c=[color], label=str(t), alpha=0.7,
                    )

                # Add legend
                self.main.ax.legend(title=f"{target} Groups")
            else:
                # Plot without grouping
                self.main.ax.scatter(
                    principal_df["PC1"], principal_df["PC2"], alpha=0.7, label="Data Points"
                )
        except Exception as e:
            raise Exception(f"Error during PCA visualization: {str(e)}")



