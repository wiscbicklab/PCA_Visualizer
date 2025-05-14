import tkinter as tk
from tkinter import filedialog, messagebox

from source.utils.constant import *
import source.utils.file_operations as file_ops



class LoadFileBox(tk.Frame):
    """
    Creates a space for a load csv file button
    """
    def __init__(self, main=None, **kwargs):
        super().__init__(main, **kwargs)

        # Declare button and label
        self.label = None
        self.button = None

        self.create_components()
        self.setup_layout()
        
    def create_components(self):
        self.label = tk.Label(self, text="Load CSV file:",
                                   **LABEL_STYLE)
        self.button = tk.Button(self, text="Browse",
                                     **BUTTON_STYLE, 
                                     command=self.load_data_file)

    def setup_layout(self):
        # Adds the label and button to the Frame
        self.label.grid(row=0, column=0, padx=5, pady=5)
        self.button.grid(row=0, column=1, padx=5, pady=5)



    #### 5. EVENT HANDLERS ####

    def handle_successful_load(self):
        """Handle successful file load."""
        self.df_updated = True
        messagebox.showinfo("Success", f"File loaded successfully: ")

    def handle_load_error(self, error: Exception):
        """Handle file loading errors."""
        messagebox.showerror("Error", f"Failed to load file: {str(error)}")



    #### 6. Data Handling ####

    def load_data_file(self):
        """Load data from CSV file."""
        self.df = file_ops.load_csv_file()

        if self.df is None or self.df.empty:
            self.handle_load_error(ValueError("File not loaded, No File Selected"))
            return
        
        self.df_loaded = True
        self.handle_successful_load()










