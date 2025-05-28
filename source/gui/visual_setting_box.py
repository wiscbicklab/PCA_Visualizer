import tkinter as tk
from tkinter import messagebox
import traceback

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
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

        # Banner
        self.banner = None

        # Target variable selection
        self.target_label = None
        self.target_dropdown = None
        self.custom_target_entry = None

        # PCA number of components selection
        self.num_pca_comp_label = None
        self.num_pca_comp_entry = None

        # Top N feature selection
        self.top_n_label = None
        self.top_n_entry = None

        # PCA analysis number selection
        # Selects which PCA component to analize loadings
        self.pca_num_label = None
        self.pca_num_entry = None

        # Text distance selection
        self.text_dist_label = None
        self.text_dist_entry = None

        # Visualization button
        self.button = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        # Creates the Banner
        self.banner = tk.Label(self, text="Visualize PCA", **BANNER_STYLE)
        
        # Creates PCA target selection
        target_options = ["None", "bbch", "Input Specific Target"]
        self.target_label = tk.Label(self, text="Target Variable:", **LABEL_STYLE)
        self.target_dropdown = tk.OptionMenu(self, self.app_state.target_mode, *target_options)
        self.target_dropdown.configure(**OPTION_MENU_STYLE)
        self.custom_target_entry = tk.Entry(
            self,
            **ENTRY_STYLE,
            state="disabled",
            textvariable=self.app_state.custom_target
        )
        self.app_state.target_mode.trace_add("write", self.toggle_entry)
        

        # Creates validation commands for the text boxes
        self.vcmd_int = (self.register(self.validate_int), '%P')
        self.vcmd_non_neg_float = (self.register(self.validate_non_neg_float), '%P')


        # Creates PCA number of components selection
        self.num_pca_comp_label = tk.Label(self, text="Number of PCA Components:", **LABEL_STYLE)
        self.num_pca_comp_entry = tk.Entry(
            self,
            **ENTRY_STYLE,
            validate="key",
            validatecommand=self.vcmd_int,
            textvariable=self.app_state.num_pca_comp
        )
        self.num_pca_comp_entry.bind("<FocusOut>", lambda e: self.on_exit(self.num_pca_comp_entry, "2", "num_pca_comp"))
        self.num_pca_comp_entry.bind("<FocusIn>", lambda e: self.on_entry(self.num_pca_comp_entry))

        # Creates top n feature selection
        self.top_n_label = tk.Label(self, text="Top N Features for Biplot:", **LABEL_STYLE)
        self.top_n_entry = tk.Entry(
            self,
            **ENTRY_STYLE ,
            validate="key",
            validatecommand=self.vcmd_int,
            textvariable=self.app_state.top_n_feat
        )
        self.top_n_entry.bind("<FocusOut>", lambda e: self.on_exit(self.top_n_entry, "10", "top_n_feat"))
        self.top_n_entry.bind("<FocusIn>", lambda e: self.on_entry(self.top_n_entry))

        # Creates top n feature selection
        self.pca_num_label = tk.Label(self, text="Select the PCA Component to Analize", **LABEL_STYLE)
        self.pca_num_entry = tk.Entry(
            self,
            **ENTRY_STYLE ,
            validate="key",
            validatecommand=self.vcmd_int,
            textvariable=self.app_state.pca_num
        )
        self.pca_num_entry.bind("<FocusOut>", lambda e: self.on_exit(self.pca_num_entry, "1", "pca_num"))
        self.pca_num_entry.bind("<FocusIn>", lambda e: self.on_entry(self.pca_num_entry))

        # Creates and input section for the Distance between text labels on generated plots
        self.text_dist_label = tk.Label(self, text="Text Distance for Labels:", **LABEL_STYLE)
        self.text_dist_entry = tk.Entry(
            self,
            **ENTRY_STYLE,
            validate="key",
            validatecommand=self.vcmd_non_neg_float,
            textvariable=self.app_state.text_dist
        )
        self.text_dist_entry.bind("<FocusOut>", lambda e: self.on_exit(self.text_dist_entry, "1.1", "text_dist"))
        self.text_dist_entry.bind("<FocusIn>", lambda e: self.on_entry(self.text_dist_entry))

        # Visualization button
        self.button = tk.Button(self, text="Visualize PCA", **BUTTON_STYLE, command=self.visualize_pca)
        
    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # PCA Parameters
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)
    
        # Target Selection Section
        self.target_dropdown.grid(row=1, column=0, columnspan=2, padx=5, pady=5,)
        self.target_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.custom_target_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.num_pca_comp_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.num_pca_comp_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.top_n_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.top_n_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        self.pca_num_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.pca_num_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        self.text_dist_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.text_dist_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # Run Analysis Buttons
        self.button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)


    #### 5. EVENT HANDLERS ####

    def toggle_entry(self, *args):
        if self.app_state.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.config(state="disabled")

    def on_entry(self, widget):
        self.original_value = float(widget.get().strip())

    def on_exit(self, widget, default_value, attr_name):
        # Get the value in the selected Attribute
        current_value = widget.get().strip()

        # Set minimum value for the selected Attribute
        if attr_name == "num_pca_comp":
            min_value = 1.9
        elif attr_name == "top_n_feat" or attr_name == "pca_num":
            min_value = 0.9
        else:
            min_value = 0.0

        # Set value to the default if it's too small
        if current_value == "" or float(current_value) <= min_value:
            widget.delete(0, tk.END)
            widget.insert(0, default_value)
            current_value = default_value

        # Set pca_num do defualt if it's too large
        if attr_name == "pca_num" and float(current_value) > float(self.app_state.num_pca_comp.get()):
            widget.delete(0, tk.END)
            widget.insert(0, default_value)
            current_value = default_value
        
        # Sets the dataFrame as updated if the related variables changed
        if float(current_value) != self.original_value:
            self.app_state.df_updated.set(True)

    def validate_int(self, proposed_value):
        # Allow user to clear input
        if proposed_value == "" or proposed_value.isdigit():
            return True 
        return False
    
    def validate_non_neg_float(self, proposed_value):
        try:
            if proposed_value == "" or float(proposed_value) >= 0:
                return True
        except Exception: pass
        return False

    #### 6. Data Handling ####

    def visualize_pca(self):
        """Creates a PCA visualization based on the given inputs and updates GUI plot"""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned in order to run PCA!")
            return  
        
        try:
            # Gets the user selected target variable
            target_mode = self.app_state.target_mode.get().strip().lower()

            if target_mode == "none":
                target = None
            elif target_mode == "bbch":
                target = "bbch"
            elif target_mode == "input specific target":
                target = self.app_state.custom_target.get()
                if not target or target.isspace():
                    messagebox.showerror("Error", f"You must enter a target variable!")
                    return
                if target not in self.app_state.df.columns.to_list():
                    messagebox.showerror("Error", f"Target variable '{target}' not found in the dataset!")
                    return
            
            # Creats a new figure and ax with labels and grid
            self.app_state.fig = Figure(self.app_state.fig_size)
            self.app_state.ax = self.app_state.fig.add_subplot(111)
            self.app_state.ax.set_xlabel("Principal Component 1")
            self.app_state.ax.set_ylabel("Principal Component 2")
            self.app_state.ax.set_title("PCA Visualization")
            self.app_state.ax.grid(True)
           
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