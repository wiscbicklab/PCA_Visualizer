# Imports needed tkinter components
import tkinter as tk
from tkinter import Radiobutton as RadBttn

# Imports constants for styling tkinter components
from ..app_state import AppState
from source.utils.constant import *

class BbchSelector(tk.Frame):
    """
    A GUI box for selecting the bbch value to filter by

    A text Header
    Radio buttons for selecting the filter
        Button for All(no filter)
        Button for BBCH 59
        Button for BBCH 69
        Button for BBCH 85
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

        # Declares Widgets for getting the user selected filter
        self.label = None
        self.none_rad = None
        self.b59_rad = None
        self.b69_rad = None
        self.b85_rad = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates BBCH label
        self.label = tk.Label(self, text="Filter by BBCH Stage:", **LABEL_STYLE)

        # Creates BBCH selection buttons
        self.none_rad = RadBttn(
            self,
            text="All (no filter)",
            value=-1,
            variable=self.app_state.bbch_choice,
            **RAD_BUTTON_STYLE
        )
        self.b59_rad = RadBttn(
            self,
            text="BBCH 59",
            value=59,
            variable=self.app_state.bbch_choice,
            **RAD_BUTTON_STYLE
        )
        self.b69_rad = RadBttn(
            self,
            text="BBCH 69",
            value=69,
            variable=self.app_state.bbch_choice,
            **RAD_BUTTON_STYLE
        )
        self.b85_rad = RadBttn(
            self,
            text="BBCH 85",
            value=85,
            variable=self.app_state.bbch_choice,
            **RAD_BUTTON_STYLE
        )

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Places BBCH label on top of this frame
        self.label.grid(row=0, padx=5, pady=5, sticky="w")

        # Places BBCH selection buttons in a column
        self.none_rad.grid(row=1, padx=5, pady=5, sticky="w")
        self.b59_rad.grid(row=2, padx=5, pady=5, sticky="w")
        self.b69_rad.grid(row=3, padx=5, pady=5, sticky="w")
        self.b85_rad.grid(row=4, padx=5, pady=5, sticky="w")

