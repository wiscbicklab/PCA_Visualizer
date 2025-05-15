import tkinter as tk
from tkinter import Radiobutton as RadBttn

from source.utils.constant import *


class BbchSelector(tk.Tk):
    """Gui Frame for asking the user what type of filter to use """
    def __init__(self, main: tk.Tk, **kwargs):
        super(main, **kwargs)
        # Gets the parent class to update data on it
        self.main = main

        self.label = None
        self.none_rad = None
        self.b59_rad = None
        self.b69_rad = None
        self.b85_rad = None

        self.create_components()
        self.setup_layout()

    def create_components(self):
        # BBCH Selection
        self.label = tk.Label(self, text="Filter by BBCH Stage:", **LABEL_STYLE)

        self.none_rad = tk.RadBttn(self, text="All (no filter)", value=-1,
                                     variable=self.main.bbch_choice, **LABEL_STYLE)
        self.b59_rad = tk.RadBttn(self, text="BBCH 59", value=59,
                                    variable=self.main.bbch_choice, **LABEL_STYLE)
        self.b69_rad = tk.RadBttn(self, text="BBCH 69", value=69,
                                    variable=self.main.bbch_choice, **LABEL_STYLE)
        self.b85_rad = tk.RadBttn(self, text="BBCH 85", value=85,
                                    variable=self.main.bbch_choice, **LABEL_STYLE)


    def setup_layout(self):
        # BBCH Selection
        self.label.grid(row=0, padx=5, pady=5, sticky="w")
        self.none_rad.grid(row=1, padx=5, pady=5, sticky="w")
        self.b59_rad.grid(row=2, padx=5, pady=5, sticky="w")
        self.b69_rad.grid(row=3, padx=5, pady=5, sticky="w")
        self.b85_rad.grid(row=4, padx=5, pady=5, sticky="w")

