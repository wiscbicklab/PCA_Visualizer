import numpy as np
from matplotlib import pyplot as plt


from source.visualization.base import BasePlotter


class ScreePlotVisualizer(BasePlotter):
    """Exact match to original scree plot functionality."""

    def create_scree_plot(self, pca_model):
        """
        Create a scree plot of explained variance.
        """
        # Ensure the figure and axes are valid
        if self.ax.figure is None:
            self.fig, self.ax = plt.subplots()

        # Remove any residual legends
        if self.ax.get_legend() is not None:
            self.ax.get_legend().remove()

        if pca_model is None:
            raise ValueError("Please run PCA analysis first.")

        # Create scree plot - exact match to original
        explained_variance = pca_model.explained_variance_ratio_

        # Bar plot of individual explained variance
        self.ax.bar(
            range(1, len(explained_variance) + 1),
            explained_variance,
            alpha=0.7,
            align='center'
        )

        # Step plot of cumulative explained variance
        self.ax.step(
            range(1, len(explained_variance) + 1),
            np.cumsum(explained_variance),
            where='mid',
            label='Cumulative explained variance'
        )

        # Labels and title - exact match
        self.ax.set_xlabel('Principal Component Index')
        self.ax.set_ylabel('Explained Variance Ratio')
        self.ax.set_title('Scree Plot')