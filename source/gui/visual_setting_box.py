import tkinter as tk
from tkinter import messagebox
import traceback

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import pandas as pd

from source.gui.app_state  import AppState

from source.utils.constant import *


class visual_setting_Box(tk.Frame):
    """
    Creates a space for PCA options
    """

    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs):
        super().__init__(main, **kwargs)
        self.main = main
        self.app_state = app_state

        # Sets the PCA analysis Target
        self.target_mode = tk.StringVar()
        self.target_mode.set("None")  # Default option

        # Banner
        self.banner = None

        # Select Target Variable Section
        self.target_label = None
        self.target_dropdown = None
        self.custom_target_entry = None

        # PCA Parameters Section
        self.components_label = None
        self.components_entry = None

        # Top N Feature User Input
        self.top_n_label = None
        self.top_n_entry = None

        # Text Distance for Labels User Input
        self.text_dist_label = None
        self.text_dist_entry = None

        # Visualization button
        self.button = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        # Creates Validation commands for the text boxes
        self.vcmd_2_or_more = (self.register(self.validate_2_or_more), '%P')
        self.vcmd_pos_int = (self.register(self.validate_pos_int), '%P')
        self.vcmd_pos_num = (self.register(self.validate_pos_num), '%P')

        # Creates the Banner
        self.banner = tk.Label(self, text="Visualize PCA", font=("Helvetica", 12),
                               bg="#dcdcdc", relief="groove")
        
        
        # Creates a dropdown value to select a PCA target
        self.target_label = tk.Label(self, text="Target Variable:", **LABEL_STYLE)
        target_options = ["None", "bbch", "Input Specific Target"]
        self.target_dropdown = tk.OptionMenu(self, self.target_mode, *target_options)
        self.target_dropdown.config(font=LABEL_STYLE["font"], bg="#007ACC", fg="white",
                                    activebackground="#005f99", relief="flat")
        # Creates an entry box to let the user enter a custom Target
        self.custom_target_entry = tk.Entry(self, **LABEL_STYLE, width=22, state="disabled")
        self.target_mode.trace_add("write", self.toggle_entry)


        # Creates an input section for the Number of PCA Components
        self.components_label = tk.Label(self, text="Number of PCA Components:", **LABEL_STYLE)
        self.components_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=22, validate="key",
                                          validatecommand=self.vcmd_2_or_more,
                                          textvariable=self.app_state.num_pca_components)
        # Sets the default value and resets the box is left empty
        self.components_entry.bind("<FocusOut>", lambda e: self.on_entry_exit(self.components_entry, "2", "num_pca_components"))

        
        # Creates and input section for the Number of features to include in the Biplot
        self.top_n_label = tk.Label(self, text="Top N Features for Biplot:", **LABEL_STYLE)
        self.top_n_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=22, validate="key", 
                                    validatecommand=self.vcmd_pos_int,
                                    textvariable=self.app_state.top_n_feat)
        # Sets the default value and resets the box is left empty
        self.top_n_entry.bind("<FocusOut>", lambda e: self.on_entry_exit(self.top_n_entry, "10", "top_n_feat"))


        # Creates and input section for the Distance between text labels on generated plots
        self.text_dist_label = tk.Label(self, text="Text Distance for Labels:", **LABEL_STYLE)
        self.text_dist_entry = tk.Entry(self, font=LABEL_STYLE["font"], width=22, 
                                            validate="key", validatecommand=self.vcmd_pos_num,
                                            textvariable=self.app_state.text_dist)
        # Sets the default value and resets the box is left empty
        self.text_dist_entry.bind("<FocusOut>", lambda e: self.on_entry_exit(self.text_dist_entry, "1.1", "text_dist"))


        # Visualization button
        self.button = tk.Button(self, text="Visualize PCA", **BUTTON_STYLE, 
                                command=self.visualize_pca)
        

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

        self.text_dist_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.text_dist_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Run Analysis Buttons
        self.button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)


    #### 5. EVENT HANDLERS ####

    def validate_2_or_more(self, proposed_value):
        # Allow user to clear input
        if proposed_value == "":
            return True 
        # Allows user to enter digits
        elif proposed_value.isdigit() and int(proposed_value) >= 2:
            self.app_state.df_updated = True
            return True
        return False

    def validate_pos_int(self, proposed_value):
        # Allow user to clear input
        if proposed_value == "":
            return True 
        # Allows user to enter digits
        elif proposed_value.isdigit() and int(proposed_value) > 0:
            self.app_state.df_updated = True
            return True
        return False
    
    def validate_pos_num(self, proposed_value):
        # Allow user to clear input
        if proposed_value == "":
            return True 
        # Allows user to enter float 0 or greater 
        try:
            value = float(proposed_value)
            if value >= 0:
                return True
        except ValueError:
            pass
        return False
    
    def toggle_entry(self, *args):
        if self.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.config(state="disabled")

    def on_entry_exit(self, widget, default_value, attr_name):
        current_value = widget.get().strip()
        if current_value == "" or float(current_value) == 0.0:
            widget.delete(0, tk.END)
            widget.insert(0, default_value)
            self.app_state.df_updated = True


    #### 6. Data Handling ####

    def visualize_pca(self):
        """Creates a PCA visualization based on the given inputs and updates GUI plot"""
        try:
            if not self.app_state.df_cleaned:
                raise Exception("Data Must be cleaned first")
            # Creats a new figure and ax with labels and grid
            self.app_state.fig = Figure()
            self.app_state.ax = self.app_state.fig.add_subplot(111)
            self.app_state.ax.set_xlabel("Principal Component 1")
            self.app_state.ax.set_ylabel("Principal Component 2")
            self.app_state.ax.set_title("PCA Visualization")
            self.app_state.ax.grid(True)

            # Gets the user selected target variable
            target_mode=self.target_mode.get().strip().lower()
            if target_mode == "none":
                target = None
            elif target_mode not in self.app_state.df.columns:
                raise ValueError(f"Target variable '{target_mode}' not found in the dataset.")
            elif target_mode == "input specific target" and not target:
                raise ValueError("Please enter a target variable.")
            elif target_mode == "bbch":
                target = "bbch"
           
            # Runs PCA Analysis and get important results
            self.app_state.main.run_analysis()
            transformed_data = self.app_state.pca_results['transformed_data']
            transformed_cols = [f'PC{i + 1}' for i in range(transformed_data.shape[1])]
            transformed_df = pd.DataFrame(transformed_data, columns=transformed_cols)


            # Plot grouped by target if available
            if target and target in self.app_state.df.columns:
                # Gets targets
                target_vals = self.app_state.df[target].reset_index(drop=True)
                unique_targets = sorted(target_vals.unique())

                # Assign colors and adds a legend
                colors = plt.cm.tab10(np.linspace(0, 1, len(unique_targets)))
                for i, t in enumerate(unique_targets):
                    mask = target_vals == t
                    color = colors[i] 
                    self.app_state.ax.scatter(transformed_df.loc[mask, "PC1"],
                                        transformed_df.loc[mask, "PC2"],
                                        c=[color], label=str(t), alpha=0.7,
                    )
                self.app_state.ax.legend(title=f"{target} Groups")
            else:
                # Plot without grouping
                self.app_state.ax.scatter(
                    transformed_df["PC1"], transformed_df["PC2"], alpha=0.7, label="Data Points"
                )

            self.app_state.main.update_figure()

        
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Visualization Error", str(e))