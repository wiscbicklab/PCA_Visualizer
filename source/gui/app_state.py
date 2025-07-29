import platform
import tkinter as tk

from matplotlib.figure import Figure




class AppState:
    def __init__(self, main):
        # Holds the main window
        self.main = main

        # Selects application color palette
        self.selected_palette = tk.StringVar(value="Default")

        # PCA Results
        self.pca_results = None

        # Output directory for saved files
        self.output_dir = "KUpca_plots_output"

        # Variables for tracking the data frame with the data file
        self.original_df = None
        self.df = None
        self.df_cleaned = tk.BooleanVar(main, value=False)
        self.df_updated = tk.BooleanVar(main, value=False)

        # Variabes to track user inputs for data cleaning
        self.missing_choice = tk.StringVar(main, value="impute_mean")
        self.bbch_choice = tk.IntVar(main, value=-1)
        self.custom_filter_target = tk.StringVar(main, value="")
        self.custom_filter_type = tk.StringVar(main, value="")

        self.custom_filter_upper = tk.StringVar(main, value="999999.99")
        self.custom_filter_lower = tk.StringVar(main, value="-999999.99")
        self.custom_filter_equal = tk.StringVar(main, value="")

        # Variables to track user inputs for plot generation
        self.pca_target = tk.StringVar(main, "")
        self.num_pca_comp = tk.IntVar(main, value=2)
        self.num_feat = tk.IntVar(main, value=10)
        self.focused_pca_num = tk.IntVar(main, value=1)
        self.heatmap_feat = tk.StringVar(main, "")
        
        # Variables for tracking feature mapping
        self.feat_group_enabled = tk.BooleanVar(main, value=False)
        self.feat_group_map = {}

        # Variables for the current figure being displayed
        self.fig_size = (10, 5)
        self.fig = Figure(self.fig_size)
        self.ax = self.fig.add_subplot(111)
        self.ax.grid(True)

        
