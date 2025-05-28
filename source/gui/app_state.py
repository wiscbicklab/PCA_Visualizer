import platform
import tkinter as tk

from matplotlib.figure import Figure




class AppState:
    def __init__(self, main):
        # Holds the main window
        self.main = main

        # Variables for tracking the data frame with the data file
        self.df = None
        self.df_loaded = tk.BooleanVar(main, value=False)
        self.df_updated = tk.BooleanVar(main, value=False)
        self.df_cleaned = tk.BooleanVar(main, value=False)

        # PCA Results
        self.pca_results = None

        # Variables for tracking feature mapping
        self.mapping_uploaded = tk.BooleanVar(main, value=False)
        self.feat_map = None
        self.feat_colors = None

        # Variables to track user inputs from the GUI
        self.num_pca_components = tk.IntVar(main, value=2)
        self.top_n_feat = tk.IntVar(main, value=10)
        self.text_dist = tk.DoubleVar(main, value=1.1)

        # Gets the name of the os
        self.os_type = platform.system()

        # Variables for tracking the figure
        self.fig_size = (8, 5)
        self.fig = Figure(self.fig_size)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)

        # Holds PCA Results
        self.pca_results = None

        # Output directory for saved files
        self.output_dir = "KUpca_plots_output"
