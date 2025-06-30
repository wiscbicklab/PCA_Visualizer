import platform
import tkinter as tk

from matplotlib.figure import Figure




class AppState:
    def __init__(self, main):
        # Holds the main window
        self.main = main

        # Gets the name of the os
        self.os_type = platform.system()

        # Selects application color palette
        self.selected_palette = tk.StringVar(value="Default")

        # PCA Results
        self.pca_results = None

        # Output directory for saved files
        self.output_dir = "KUpca_plots_output"

        # Variables for tracking the data frame with the data file
        self.df = None
        self.df_cleaned = tk.BooleanVar(main, value=False)
        self.df_updated = tk.BooleanVar(main, value=False)

        # Varialbe to track user inputs for data cleaning
        self.missing_choice = tk.StringVar(main, value="impute_mean")
        self.bbch_choice = tk.IntVar(main, value=-1)

        # Variables to track user inputs for plot generation
        self.target_mode = tk.StringVar(main, "None")
        self.custom_target = tk.StringVar(main, "")
        self.num_pca_comp = tk.IntVar(main, value=2)
        self.top_n_feat = tk.IntVar(main, value=10)
        self.pca_num = tk.IntVar(main, value=1)
        self.text_dist = tk.DoubleVar(main, value=1.1)

        # Variables for tracking feature mapping
        self.feat_group_enable = tk.BooleanVar(main, value=False)
        self.feat_group_map = None
        self.group_color_map = None

        # Variables for the current figure being displayed
        self.fig_size = (8, 5)
        self.fig = Figure(self.fig_size)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)

        
