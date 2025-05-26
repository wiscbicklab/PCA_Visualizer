import tkinter as tk
from tkinter import  messagebox

from matplotlib.figure import Figure

import source.utils.file_operations as file_ops
from source.utils.constant import *

from source.gui.app_state  import AppState


class LoadFileBox(tk.Frame):
    """
    Creates a space for Biplot generation buttons.
    
    Parameters:
        fig : matplotlib.figure.Figure
            The figure to which the biplot will be added.
        main : tk.Widget, optional
            The parent widget for this frame.
        **kwargs : dict
            Additional keyword arguments passed to tk.Frame.
    """
    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs: dict):
        super().__init__(main, **kwargs)
        self.app_state = app_state


        self.label = None
        self.button = None

        self.create_components()
        self.setup_layout()
        
    def create_components(self):
        """
        Creates all the components to be used within this Widget
        """
        self.label = tk.Label(self, text="Load CSV file:", **LABEL_STYLE)
        self.button = tk.Button(self, text="Browse", **BUTTON_STYLE, command=self.load_data)
                                     

    def setup_layout(self):
        """
        Places components within the Widget
        """
        # Configure column expansion
        self.columnconfigure(1, weight=1)

        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.button.grid(row=0, column=1, padx=5, pady=5)


    #### 6. Data Handling ####

    def load_data(self):
        """
        Load data from CSV file and update status variable in the main Widget
        """
        # Load Data from File
        self.app_state.df = file_ops.load_csv_file()

        # Show Error message and set df status variables if the file failed to load
        if self.app_state.df is None or self.app_state.df.empty:
            messagebox.showerror("Error", "Failed to load file!")
            self.app_state.df_loaded.set(False)
            self.app_state.df_cleaned.set(False)
            return

        self.app_state.df_updated.set(True)
        self.app_state.df_loaded.set(True)
        self.app_state.df_cleaned.set(False)

        # Generate new Blank figure
        self.app_state.fig = Figure()
        self.app_state.ax = self.app_state.fig.add_subplot(111)
        self.app_state.ax.grid(True)
        
        # Tells the container Widget do update the displayed data
        self.app_state.main.update_data_info()

        # Show Success message and set df status variables after the file loads
        messagebox.showinfo("Success", "File loaded successfully")

