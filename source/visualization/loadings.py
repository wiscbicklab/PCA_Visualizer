import numpy as np
from tkinter import messagebox

from matplotlib import pyplot as plt


class LoadingsProcessor:
    """Processes and validates PCA loadings data for visualization."""

    def __init__(self, pca_model, data):
        self.pca_model = pca_model
        self.data = data
        self.fig, self.ax = None, None

    def validate_and_get_loadings(self, heatmap_mode, focus_entry=None):
        """
        Validates PCA model and retrieves loadings based on mode.

        Args:
            heatmap_mode (str): Mode to determine which features to focus on.
            focus_entry (str): Comma-separated column names for custom focus (optional).

        Returns:
            Tuple[np.ndarray, List[str]]: Loadings array and list of focus columns.
        """
        # Validate PCA model
        if self.pca_model is None or not hasattr(self.pca_model, 'components_'):
            messagebox.showerror("Error", "Please run PCA analysis first.")
            return None, None

        # Initialize or reset figure and axes
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=100) if self.fig is None else self.ax.clear()

        try:
            # Extract loadings
            loadings = self.pca_model.components_.T
            feature_scores = np.abs(loadings[:, 0])  # Example: PC1 loadings

            # Determine focus columns based on mode
            if "Top" in heatmap_mode:
                top_n = int(heatmap_mode.split()[1])  # Extract number from mode
                top_indices = np.argsort(feature_scores)[::-1][:top_n]
                focus_columns = [self.data.columns[i] for i in top_indices]
            elif heatmap_mode == "Custom" and focus_entry:
                focus_columns = [col.strip() for col in focus_entry.split(",") if col.strip()]
                if not all(col in self.data.columns for col in focus_columns):
                    raise ValueError("Some specified columns do not exist in the dataset.")
            else:
                raise ValueError("Invalid heatmap mode or missing focus entry.")

            return loadings, focus_columns

        except Exception as e:
            messagebox.showerror("Error", f"Error processing loadings: {str(e)}")
            return None, None