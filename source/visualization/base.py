import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import Normalize
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Ellipse
from scipy import stats
import plotly.graph_objects as go
import plotly.io as pio
from adjustText import adjust_text
import os
import time
from tkinter import messagebox


class BasePlotter:
    """Base class maintaining exact matplotlib setup from original."""

    def __init__(self, fig=None, ax=None):
        self.fig = fig if fig else plt.Figure(figsize=(5, 5), dpi=100)
        self.ax = ax if ax else self.fig.add_subplot(111)

    def clear_plot(self):
        """Match original plot clearing behavior."""
        self.ax.clear()
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

    def update_figure(self, canvas):
        """Match original canvas update."""
        canvas.draw()

    def save_plot(self, output_dir):
        """Preserve original save functionality."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        plot_filename = f'plot_{timestamp}.png'
        save_path = os.path.join(output_dir, plot_filename)
        try:
            self.fig.savefig(save_path)
            return save_path
        except Exception as e:
            raise Exception(f"Could not save the plot: {str(e)}")