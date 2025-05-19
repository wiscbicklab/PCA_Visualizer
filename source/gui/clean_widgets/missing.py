import tkinter as tk
from tkinter import Radiobutton as RadBttn

from source.utils.constant import *



class MissingSelector(tk.Frame):
    """Gui Frame for asking the user how they would like to deal with missing data."""
    def __init__(self, main: tk.Tk, **kwargs):
        super().__init__(main, **kwargs)
        # Gets the parent class to update data on it
        self.main = main

        self.label = None
        self.mean_rad = None
        self.median_rad = None
        self.nan_rad = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Create all tkinter widgets and components for the interface."""
        self.label = tk.Label(self,text="Handle Missing Values:", **LABEL_STYLE)
        
        self.mean_rad = RadBttn(self, text="Impute with Mean", value="impute_mean",
                                         variable=self.main.missing_choice,  **RAD_BUTTON_STYLE)
        self.median_rad = RadBttn(self,text="Impute with Median", value="impute_median",
                                           variable=self.main.missing_choice, **RAD_BUTTON_STYLE)
        self.nan_rad = RadBttn(self, text="Replace NaN with 0", value="replace_nan",
                                        variable=self.main.missing_choice, **RAD_BUTTON_STYLE)


    def setup_layout(self):
        """Creates the layout of this Widget"""
        self.label.grid(row=0, padx=5, pady=5, sticky="w")
        self.mean_rad.grid(row=1, padx=5, pady=5, sticky="w")
        self.median_rad.grid(row=2, padx=5, pady=5, sticky="w")
        self.nan_rad.grid(row=3, padx=5, pady=5, sticky="w")

