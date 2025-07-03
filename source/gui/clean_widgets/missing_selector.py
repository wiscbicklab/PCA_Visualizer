# Imports needed tkinter components
import tkinter as tk
from tkinter import Radiobutton as RadBttn

# Imports constants for styling tkinter components
from source.gui.app_state import AppState
from source.utils.constant import *


class MissingSelector(tk.Frame):
    """
    A GUI box for selecting how to handle missing values in the data

    A text Header
    Radio buttons for selecting the filter
        Button for Imputing with Mean
        Button for Imputing with Median
        Button for Replacing with 0
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main: tk.Tk, app_state: AppState,  **kwargs):
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

        # Declares widgets for getting user interpolation selection
        self.label = None
        self.mean_rad = None
        self.median_rad = None
        self.nan_rad = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates interpolation label
        self.label = tk.Label(self,text="Handle Missing Values:", **LABEL_STYLE)
        
        # Creates interploation selection buttons
        self.mean_rad = RadBttn(
            self,
            text="Impute with Mean",
            value="impute_mean",
            variable=self.app_state.missing_choice,
            **RAD_BUTTON_STYLE
        )
        self.median_rad = RadBttn(
            self,
            text="Impute with Median",
            value="impute_median",
            variable=self.app_state.missing_choice,
            **RAD_BUTTON_STYLE
        )
        self.nan_rad = RadBttn(
            self,
            text="Replace NaN with 0",
            value="replace_nan",
            variable=self.app_state.missing_choice,
            **RAD_BUTTON_STYLE
        )

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Places interpolation label at the top of this frame
        self.label.grid(row=0, padx=5, pady=5, sticky="w")

        # Places interpolation selection buttons in a column
        self.mean_rad.grid(row=1, padx=5, pady=5, sticky="w")
        self.median_rad.grid(row=2, padx=5, pady=5, sticky="w")
        self.nan_rad.grid(row=3, padx=5, pady=5, sticky="w")

