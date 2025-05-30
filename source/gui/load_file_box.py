import tkinter as tk
from tkinter import  messagebox
from tkinter import filedialog

import chardet
import pandas as pd

from source.utils.constant import *

from source.gui.app_state  import AppState


class LoadFileBox(tk.Frame):
    """
    Creates a space for Biplot generation buttons.
    
    Args:
        main: tk.Widget
            The parent widget for this frame.
        app_state: AppState
            The app_state variable used to pass data between components
        **kwargs: dict
            Additional keyword arguments passed to tk.Frame.
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs: dict):
        """Initializes box for cleaning user data"""
        # Intializes data about the container class
        super().__init__(main, **kwargs)
        self.app_state = app_state

        # Declares components
        self.label = None
        self.button = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()
        
    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates components
        self.label = tk.Label(self, text="Load CSV file:", **LABEL_STYLE)
        self.button = tk.Button(self, text="Browse", **BUTTON_STYLE, command=self.load_data)
    
    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure column expansion
        self.columnconfigure(1, weight=1)

        # Places components
        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.button.grid(row=0, column=1, padx=5, pady=5)


    #### 1. Data Handling ####

    def load_data(self):
        """Asks user to select a .csv data file and loads the data from the selected file"""
        # Asks user to select a csv file
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

        # Ensures the user selected an appropriate file
        if not file_path:
            messagebox.showerror("File Error", "No file was selected. File loadings aborted!")
            return
        if not file_path.lower().endswith(".csv"):
            messagebox.showerror("File Error", f"You selected: {file_path}\nYou must select a .csv file instead!")
            return

        # Attempts to load user data file
        try:
            with open(file_path, 'rb') as file:
                result = chardet.detect(file.read())
            encoding = result['encoding']
            self.app_state.df = pd.read_csv(file_path, encoding=encoding)
        except OSError as e:
            print(e.strerror)
            messagebox.showerror("File Error", f"An error occurred while opening the file: {e}")
            return

        # Check that the data has been loaded correctly
        if self.app_state.df is None or self.app_state.df.empty:
            self.app_state.df_loaded.set(False)
            self.app_state.df_cleaned.set(False)
            messagebox.showerror("Loadings Error", "File was opened, but no data was found!")
            return

        # Updates df status variables
        self.app_state.df_updated.set(True)
        self.app_state.df_loaded.set(True)
        self.app_state.df_cleaned.set(False)

        # Generate new blank figure
        self.app_state.main.create_blank_fig()
        

        
        #DEBUGGING CONSOLE PRINTOUT
        print("DataFrame Shape:\t" + self.app_state.df.shape)
        print("DataFrame Head:\t" + self.app_state.df.head())
        print("DataFrame Column Names:\t" + self.app_state.df.columns)

        

        # Updates the GUI and shows sucess message
        self.app_state.main.update_data_info()
        messagebox.showinfo("Success", "File loaded successfully")

