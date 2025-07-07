import tkinter as tk
from tkinter import messagebox

from source.gui.app_state  import AppState
from source.utils.constant import *
import source.utils.input_validation as vcmd

class FilterSelector(tk.Frame):
    """
    A GUI box for selecting the bbch value to filter by

    A text Header
    A text-box for selecting the data column to filter by
    A dropdown menu for the type of filtering to use
    A text-box for the lower bound filter
    A text-box for the upper bound filter
    A text-box for exact filtering
    """
    
    #### 0. Setup GUI Elements ####
    
    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs):
        """
        Creates a space for selecting BBCH filtering
        
        Parameters:
            main: tk.Widget
                The parent widget for this frame.
            app_state: AppState
                The app_state variable used to pass data between components
            **kwargs: dict
                Additional keyword arguments passed to tk.Frame.
        """
        # Intializes data about the container class
        super().__init__(main, **kwargs)
        self.app_state = app_state

        # Decleares Filter Type Selector
        self.filter_type_lbl = None
        self.filter_type_menu = None

        # Declares Filter Target Selector
        self.target_lbl = None
        self.target_entry = None

        # Declares filtering inputs
        self.upper_lbl=None
        self.upper_entry = None
        self.lower_lbl = None
        self.lower_entry = None
        self.equal_lbl = None
        self.equal_entry = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates filter type selector
        self.filter_type_lbl = tk.Label(self, text="Filter Type: ", **LABEL_STYLE)
        filters = ["None", "Equal to", "Less than", "Greater than", "Less than and Greater than", "Less than or Greater than"]
        self.filter_type_menu = tk.OptionMenu(
            self,
            self.app_state.custom_filter_type,
            *filters,
            command=self.update_filter_entries,
        )
        self.app_state.custom_filter_type.set(filters[0])

        # Creates filter target entry
        self.target_lbl = tk.Label(self, text="Data Column: ", **LABEL_STYLE)
        self.target_entry = tk.Entry(
            self,
            **SMALL_ENTRY_STYLE ,
            textvariable=self.app_state.custom_filter_target,
            state="readonly",
        )

        # Creates filtering entries
        self.upper_entry = tk.Entry(
            self,
            **SMALL_ENTRY_STYLE,
            validate="key",
            validatecommand=(self.register(vcmd.validate_float_format), '%P'),
            textvariable=self.app_state.custom_filter_upper,
            state="readonly"
        )
        self.upper_entry.bind("<FocusOut>", lambda e: self._on_exit_upper_entry(999999.99))
        self.lower_entry = tk.Entry(
            self,
            **SMALL_ENTRY_STYLE,
            validate="key",
            validatecommand=(self.register(vcmd.validate_float_format), '%P'),
            textvariable=self.app_state.custom_filter_lower,
            state="readonly"
        )
        self.lower_entry.bind("<FocusOut>", lambda e: self._on_exit_lower_entry(-999999.99))
        self.equal_entry = tk.Entry(
            self,
            **SMALL_ENTRY_STYLE,
            textvariable=self.app_state.custom_filter_equal,
            state="readonly"
        )
        self.equal_entry.bind("<FocusOut>", lambda e: self._on_exit_equal_exit())

        # Creates text for filtering entries
        self.upper_lbl = tk.Label(self, text="Upper Bound: ", **LABEL_STYLE)
        self.lower_lbl = tk.Label(self, text="Lower Bound: ", **LABEL_STYLE)
        self.equal_lbl = tk.Label(self, text="Values: ", **LABEL_STYLE)
        

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Places Filter Type Selector
        self.filter_type_lbl.grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.filter_type_menu.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Places Filter Target selector
        self.target_lbl.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.target_entry.grid(row=1, column=1, padx=5, pady=5, sticky='w')        

        # Places Filter Parameter Selectors
        self.upper_lbl.grid(row=3, column=0,  padx=5, pady=5, sticky="e")
        self.upper_entry.grid(row=3, column=1,  padx=5, pady=5, sticky="w")
        self.lower_lbl.grid(row=4, column=0,  padx=5, pady=5, sticky="e")
        self.lower_entry.grid(row=4, column=1,  padx=5, pady=5, sticky="w")
        self.equal_lbl.grid(row=5, column=0,  padx=5, pady=5, sticky="e")
        self.equal_entry.grid(row=5, column=1,  padx=5, pady=5, sticky="w")


    #### 1. Event Handlers ####

    def update_filter_entries(self, *args):
        filter_type = self.app_state.custom_filter_type.get()

        if filter_type == "None":
            self.target_entry.config(state="readonly")
            self.upper_entry.config(state="readonly")
            self.lower_entry.config(state="readonly")
            self.equal_entry.config(state="readonly")

        elif filter_type == "Equal to":
            self.target_entry.config(state="normal")
            self.upper_entry.config(state="readonly")
            self.lower_entry.config(state="readonly")
            self.equal_entry.config(state="normal")

        elif filter_type == "Less than":
            self.target_entry.config(state="normal")
            self.upper_entry.config(state="normal")
            self.lower_entry.config(state="readonly")
            self.equal_entry.config(state="readonly")

        elif filter_type == "Greater than":
            self.target_entry.config(state="normal")
            self.upper_entry.config(state="readonly")
            self.lower_entry.config(state="normal")
            self.equal_entry.config(state="readonly")

        elif filter_type == "Less than and Greater than":
            self.target_entry.config(state="normal")
            self.upper_entry.config(state="normal")
            self.lower_entry.config(state="normal")
            self.equal_entry.config(state="readonly")

        elif filter_type == "Less than or Greater than":
            self.target_entry.config(state="normal")
            self.upper_entry.config(state="normal")
            self.lower_entry.config(state="normal")
            self.equal_entry.config(state="readonly")

        else:
            messagebox.showerror("Application Error", "An internal program error has occured trying to get the filter type")

    def _on_exit_upper_entry(self, default_value):
        """Validates that the upper entry value is a float during exit"""
        value = self.app_state.custom_filter_upper.get()
        if not vcmd.validate_float(value):
            self.app_state.custom_filter_upper.set(str(default_value))

    def _on_exit_lower_entry(self, default_value):
        """Validates that the lower entry value is a float during exit"""
        value = self.app_state.custom_filter_lower.get()
        if not vcmd.validate_float(value):
            self.app_state.custom_filter_lower.set(default_value)

    def _on_exit_equal_exit(self   ):
        """Validates that the equel entry value is alist of floats during exit"""
        # Gets the user input and splits it into a list using commas as seperators
        text_entry = self.app_state.custom_filter_equal.get()
        values = [val.strip() for val in text_entry.split(",") if val.strip()]

        # Creates filtered text to override user input with only value that are floats
        filtered_text_entry = ""
        for value in values:
            if vcmd.validate_float(value):
                filtered_text_entry = filtered_text_entry + value + ","
        
        if len(filtered_text_entry) > 0:
            filtered_text_entry = filtered_text_entry[: -1]

        # Sets the user input variable to the filtered text
        self.app_state.custom_filter_equal.set(filtered_text_entry)


