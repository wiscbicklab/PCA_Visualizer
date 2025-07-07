import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
import traceback

from matplotlib import cm
from matplotlib.colors import to_hex
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

        # Declares feature mapping components
        self.mapping_toggle = None
        self.mapping_label = None
        self.mapping_bttn = None

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
            **BIG_ENTRY_STYLE,
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
            **BIG_ENTRY_STYLE,
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
            **BIG_ENTRY_STYLE ,
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
            **BIG_ENTRY_STYLE ,
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
            **BIG_ENTRY_STYLE,
            validate="key",
            validatecommand=self.vcmd_non_neg_float,
            textvariable=self.app_state.text_dist
        )
        self.text_dist_entry.bind("<FocusOut>", lambda e: self.on_exit(self.text_dist_entry, "1.1", "text_dist"))
        self.text_dist_entry.bind("<FocusIn>", lambda e: self.on_entry(self.text_dist_entry))
        self.text_dist_entry.bind("<Return>", lambda e: self.text_dist_entry.tk_focusNext().focus())

        # Creates feature mapping components
        self.mapping_toggle = tk.Checkbutton(
            self,
            text="Enable Feature Grouping",
            variable=self.app_state.feat_group_enable,
            command=self.update_mapping_bttn,
            **LABEL_STYLE,
        )
        self.mapping_label = tk.Label(self, **LABEL_STYLE, text="Feature Grouping Map:")
        self.mapping_bttn = tk.Button(self, text="Browse", **BUTTON_STYLE, command=self.upload_mapping, state="disabled")
        
    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Places banner at top of this component
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Places feature grouping components
        self.mapping_toggle.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.mapping_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.mapping_bttn.grid(row=2, column=1, padx=5, pady=5, sticky='w')
    
        # Places target selection widgets
        self.target_mode_label.grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.target_mode_dropdown.grid(row=3, column=1, padx=5, pady=5, sticky='w')
        self.custom_target_label.grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.custom_target_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        # Places selector for number of PCA components
        self.num_pca_comp_label.grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.num_pca_comp_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Places selector for number of top PCA features
        self.top_n_label.grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.top_n_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")

        # Places selector for PCA component to analise
        self.pca_num_label.grid(row=7, column=0, padx=5, pady=5, sticky="e")
        self.pca_num_entry.grid(row=7, column=1, padx=5, pady=5, sticky="w")

        # Places selector for label text distances
        self.text_dist_label.grid(row=8, column=0, padx=5, pady=5, sticky="e")
        self.text_dist_entry.grid(row=8, column=1, padx=5, pady=5, sticky="w")

        


    #### 1. EVENT HANDLERS ####

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

    def update_mapping_bttn(self):
        """Toggles the mapping button state"""
        if self.app_state.feat_group_enable.get():
            self.mapping_bttn.config(state='normal')
        else:
            self.mapping_bttn.config(state='disabled')

    #### 2. Feature Grouping Operations ####

    def upload_mapping(self):
        """Allow the user to upload a mapping CSV file for feature-to-group mapping."""
        # Asks the user to select a csv file and ensures a csv file was selected
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            messagebox.showerror("Error", "No file selected. Please upload a valid mapping CSV.")
            return
        if not file_path.lower().endswith(".csv"):
            messagebox.showerror("File Error", f"The selected file: {file_path} is not a csv file. You must select a CSV file")
            return

        try:
            # Load the CSV into a DataFrame and set column names to lower case
            df = pd.read_csv(file_path)
            df.columns = df.columns.str.lower()


            # Validate input DataFrame
            if "feature" not in df.columns.to_list() or "group" not in df.columns.to_list():
                messagebox.showerror("Error", "Invalid Feature File, 'Feature' or 'Group' column not found")
                return

            # Create feature-to-group mapping and standardize to lowercase
            self.app_state.feat_group_map = {
                key.lower(): value.lower() for key, value in zip(df["feature"], df["group"])
            }

            # Get unique groups
            unique_groups = sorted(df['group'].unique())

            # Generate a dynamic color palette for groups
            colormap = cm.get_cmap('tab20', len(unique_groups))  # Use a colormap with sufficient distinct colors
            self.app_state.group_color_map = {
                group: to_hex(colormap(i)) for i, group in enumerate(unique_groups)
            }

            messagebox.showinfo("Success", "Feature-to-Group mapping loaded successfully.")
        
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")



