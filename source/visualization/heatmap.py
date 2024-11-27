import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt
from tkinter import messagebox

class LoadingsHeatmapVisualizer:
    def __init__(self, fig, ax):
        self.fig = fig
        self.ax = ax

    def display_loadings_heatmap(self, loadings, data_columns, focus_columns=None, cmap='viridis'):
        """
        Display a heatmap of loadings with improved design.
        :param loadings: PCA loadings matrix
        :param data_columns: List of all data column names
        :param focus_columns: List of columns to focus on (optional)
        :param cmap: Colormap for heatmap
        """
        if focus_columns is None:
            focus_columns = data_columns  # Default to all columns if none specified

        # Select only the relevant rows from the loadings matrix
        selected_loadings = loadings[[data_columns.index(col) for col in focus_columns], :]

        # Create the heatmap
        plt.figure(figsize=(10, 12))  # Increase figure size for clarity
        sns.heatmap(
            selected_loadings,
            annot=True,  # Add annotations to cells
            fmt=".2f",  # Format numbers
            cmap=cmap,  # Use perceptually uniform colormap
            cbar_kws={'label': 'Absolute Loadings'},  # Single, descriptive colorbar
            xticklabels=[f'PC{i + 1}' for i in range(selected_loadings.shape[1])],
            yticklabels=focus_columns,
            ax=self.ax
        )

        # Improve plot aesthetics
        self.ax.set_title('Loadings Heatmap', fontsize=16)
        self.ax.tick_params(axis='x', labelsize=12)
        self.ax.tick_params(axis='y', labelsize=10)
        self.ax.set_xlabel('Principal Components', fontsize=14)
        self.ax.set_ylabel('Features', fontsize=14)

        # Adjust layout
        plt.tight_layout()