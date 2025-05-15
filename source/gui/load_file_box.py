import tkinter as tk
from tkinter import  messagebox

import source.utils.file_operations as file_ops
from source.utils.constant import *


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
    def __init__(self, main: tk.Tk, **kwargs: dict):
        super().__init__(main, **kwargs)
        self.main = main

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
        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.button.grid(row=0, column=1, padx=5, pady=5)


    #### 6. Data Handling ####

    def load_data(self):
        """
        Load data from CSV file and update status variable in the main Widget
        """
        # Load Data from File
        self.main.df = file_ops.load_csv_file()

        # Show Error message and set df status variables if the file failed to load
        if self.main.df is None or self.main.df.empty:
            messagebox.showerror("Error:\tFailed to load file!")
            self.main.df_loaded = False
            self.main.df_clean = False
            return
            
        # Show Success message and set df status variables after the file loads
        messagebox.showinfo("Success", f"File loaded successfully: ")
        self.main.df_updated = True
        self.main.df_loaded = True
        return True

