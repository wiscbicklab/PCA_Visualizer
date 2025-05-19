import platform
import tkinter as tk

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg




class AppState:
    def __init__(self, main):
        # Holds the main window
        self.main = main

        # Variables for tracking the data frame with the data file
        self.df = None
        self.df_loaded = tk.BooleanVar(main, value=False)
        self.df_updated = tk.BooleanVar(main, value=False)
        self.df_cleaned = tk.BooleanVar(main, value=False)

        # Variables for visualizing pca results
        self.pca_results = None
        self.feature_to_group = None
        self.feature_groups_colors = None

        # Variables to track user inputs from the GUI
        self.num_pca_components = tk.IntVar(main, value=2)
        self.top_n_feat = tk.IntVar(main, value=10)
        self.test_dist = tk.DoubleVar(main, value=1.1)

        # Gets the name of the os
        self.os_type = platform.system()

        # Variables for tracking the figure
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        # Adds a grid to the figure
        self.ax.grid(True)

        # Holds PCA Results
        self.pca_results
