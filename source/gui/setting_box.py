import tkinter as tk
from tkinter import messagebox
import traceback

from matplotlib import pyplot as plt
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from source.gui.app_state  import AppState
from source.utils.constant import *


class SettingBox(tk.Frame):
    """
    A GUI box for holding selection settings for PCA analysis and other plot generation

    A banner with a header for the section
    Two columns, one for text labels and one for entries
        * "Target Variable" and a dropdown menu
        * "Custom Target Variable" and an entry box
        * "Number of PCA Components" and an entry box
        * "Top N Features for Biplot" and an entry bow
        * "Select the PCA Component to Analize" and an entry box
        * "Text Distance for Labels" and an entry box
    A button for creating and visualizing a PCA plot
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs):
        """
        Creates a space for plot settings and visualizing PCA analysis

        Args:
            main: tk.Widget
                The parent widget for this frame.
            app_state: AppState
                The app_state variable used to pass data between components
            **kwargs: dict
                Additional keyword arguments passed to tk.Frame.
        """
        super().__init__(main, **kwargs)
        self.main = main
        self.app_state = app_state

        # Declares frame banner
        self.banner = None

        # Declares target selection components
        self.target_mode_label = None
        self.target_mode_dropdown = None
        self.custom_target_label = None
        self.custom_target_entry = None

        # Declares selector for the number of PCA components
        self.num_pca_comp_label = None
        self.num_pca_comp_entry = None

        # Declares selector for number of top PCA features
        self.top_n_label = None
        self.top_n_entry = None

        # Declares selector for PCA component to analize
        self.pca_num_label = None
        self.pca_num_entry = None

        # Declares Selector for text distance labels 
        self.text_dist_label = None
        self.text_dist_entry = None

        # Declares button for visualizing PCA
        self.button = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates the Banner
        self.banner = tk.Label(self, text="Settings", **BANNER_STYLE)
        
        # Creates compnents for seleting the target variable 
        self.target_mode_label = tk.Label(self, text="Target Variable:", **LABEL_STYLE)
        self.target_mode_dropdown = tk.OptionMenu(
            self,
            self.app_state.target_mode, 
            "None",
            "bbch",
            "Input Specific Target",
        )
        self.target_mode_dropdown.configure(**OPTION_MENU_STYLE)
        self.custom_target_label = tk.Label(self, text="Custom Target Variable:", **LABEL_STYLE)
        self.custom_target_entry = tk.Entry(
            self,
            **ENTRY_STYLE,
            state="disabled",
            textvariable=self.app_state.custom_target
        )
        self.app_state.target_mode.trace_add("write", self.toggle_custom_target_entry)
        
        # Creates validation commands for the text boxes
        self.vcmd_int = (self.register(self.validate_int), '%P')
        self.vcmd_non_neg_float = (self.register(self.validate_non_neg_float), '%P')

        # Creates components for selecting the number of PCA components
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
        self.num_pca_comp_entry.bind("<Return>", lambda e: self.num_pca_comp_entry.tk_focusNext().focus())

        # Creates components for selecting the number of top PCA features
        self.top_n_label = tk.Label(self, text="Number of Features:", **LABEL_STYLE)
        self.top_n_entry = tk.Entry(
            self,
            **ENTRY_STYLE ,
            validate="key",
            validatecommand=self.vcmd_int,
            textvariable=self.app_state.num_feat
        )
        self.top_n_entry.bind("<FocusOut>", lambda e: self.on_exit(self.top_n_entry, "10", "top_n_feat"))
        self.top_n_entry.bind("<FocusIn>", lambda e: self.on_entry(self.top_n_entry))
        self.top_n_entry.bind("<Return>", lambda e: self.top_n_entry.tk_focusNext().focus())


        # Creates components for selecting which PCA component to analise
        self.pca_num_label = tk.Label(self, text="Focused PCA Component:", **LABEL_STYLE)
        self.pca_num_entry = tk.Entry(
            self,
            **ENTRY_STYLE ,
            validate="key",
            validatecommand=self.vcmd_int,
            textvariable=self.app_state.focused_pca_num
        )
        self.pca_num_entry.bind("<FocusOut>", lambda e: self.on_exit(self.pca_num_entry, "1", "pca_num"))
        self.pca_num_entry.bind("<FocusIn>", lambda e: self.on_entry(self.pca_num_entry))
        self.pca_num_entry.bind("<Return>", lambda e: self.pca_num_entry.tk_focusNext().focus())


        # Creates components for selecting the label text distance
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
        self.text_dist_entry.bind("<Return>", lambda e: self.text_dist_entry.tk_focusNext().focus())


        # Creates button for visualizing PCA plot
        self.button = tk.Button(self, text="Visualize PCA", **BUTTON_STYLE, command=self.visualize_pca)
        
    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Places banner at top of this component
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)
    
        # Places target selection widgets
        self.target_mode_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.target_mode_dropdown.grid(row=1, column=1, padx=5, pady=5, sticky='w')
        self.custom_target_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.custom_target_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Places selector for number of PCA components
        self.num_pca_comp_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.num_pca_comp_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Places selector for number of top PCA features
        self.top_n_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.top_n_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Places selector for PCA component to analise
        self.pca_num_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.pca_num_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Places selector for label text distances
        self.text_dist_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.text_dist_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # Places PCA Visualization button
        self.button.grid(row=8, column=0, columnspan=2, padx=5, pady=5)


    #### 1. VISUALIZATION METHODS ####

    def visualize_pca(self):
        """
        Creates a PCA visualization based on the given inputs and updates GUI plot
        
        Creates a PCA plot of the first two prinicple components. Creates groupings using
            the selected Target Variable and gives them unique colors. Displays the generated plot.
        """
        # Validates that the data has been cleaned
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned in order to run PCA.")
            return  
        
        # Runs PCA Analysis and get important results
        self.app_state.main.run_analysis()
        transformed_data = self.app_state.pca_results['transformed_data']
        transformed_cols = [f'PC{i + 1}' for i in range(transformed_data.shape[1])]
        transformed_df = pd.DataFrame(transformed_data, columns=transformed_cols)
        
        # Gets the user selected target variable
        target = self.get_target()

        # Generate new blank figure
        self.app_state.main.create_blank_fig()
        # Adds title and axis lables to the figure
        self.app_state.ax.set_title("PCA Visualization")
        self.app_state.ax.set_xlabel("Principal Component 1")
        self.app_state.ax.set_ylabel("Principal Component 2")

        # Plot grouped by target if available
        if target:
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

    def get_target(self):
        """
        Gets the user selected target
        
        Returns:
            None if None is selected, the selected target is not in the df, or an error occures
            Otherwise the selected target stripped of whitespace and in lower case
        """
        # Get the user selected target mode
        target_mode = self.app_state.target_mode.get().strip().lower()

        # Determines the target given the target mode
        if target_mode == "none":
            return None
        elif target_mode == "bbch":
            if target_mode in self.app_state.df.columns.to_list():
                return "bbch"
            else:
                messagebox.showerror(
                    "Target Error",
                    f"BBCH selected as target, but not found in the dataset!"
                )
                return None
        elif target_mode == "input specific target":
            # If the target mode is a custom target get the user specified target
            target = self.app_state.custom_target.get().strip().lower()
            if not target or target.isspace():
                messagebox.showerror(
                    "Target Error",
                    f"Invalid target selected.\nDefaulting to no target."
                )
                return None
            if target not in self.app_state.df.columns.to_list():
                messagebox.showerror(
                    "Target Error",
                    f"Target variable '{target}' not found in the dataset!\nDefualting to no target."
                )
                return None
            return target.strip().lower()
        else:
            messagebox.showerror(
                "Target_Mode Error",
                f"An internal application error occured, an impossible target_mode was selected!"
            )
            return None


    #### 2. EVENT HANDLERS ####

    def toggle_custom_target_entry(self, *args):
        """Toggles the custom_target_entry to accept or refuse input"""
        if self.app_state.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.config(state="disabled")

    def on_entry(self, widget):
        """Command for saving input value of entry option upon enter"""
        self.original_value = float(widget.get().strip())

    def on_exit(self, widget, default_value, attr_name):
        """Command for verifiying entry option value upon exit"""
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
        if current_value == "" or current_value == "." or float(current_value) <= min_value:
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
        """Validate that user iput is an integer or is blank"""
        if proposed_value == "" or proposed_value.isdigit():
            return True 
        return False
    
    def validate_non_neg_float(self, proposed_value):
        """Validates that user input is in float format"""
        try:
            if proposed_value == "" or proposed_value == "." or float(proposed_value) >= 0:
                return True
        except Exception: pass
        return False


