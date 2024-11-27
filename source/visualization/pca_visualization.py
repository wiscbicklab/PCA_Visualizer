import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from source.visualization.base import BasePlotter


class PCAVisualizer(BasePlotter):

    def plot(self, principal_components, data, target_mode, target=None):
        """
        Visualize PCA results.
        """
        self.clear_plot()

        try:
            # Convert principal_components to DataFrame
            principal_df = pd.DataFrame(
                principal_components,
                columns=[f'PC{i + 1}' for i in range(principal_components.shape[1])],
            )

            # Determine target variable
            if target_mode == "bbch":
                target = "bbch"
            elif target_mode == "input specific target":
                if not target:
                    raise ValueError("Please enter a target variable.")
            else:
                target = None

            # Plot grouped by target if available
            if target and target in data.columns:
                target_vals = data[target]
                unique_targets = sorted(target_vals.unique())

                # Assign colors dynamically
                if target == "bbch":
                    colors = {"B59": "red", "B69": "blue", "B85": "green"}
                else:
                    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_targets)))

                for i, t in enumerate(unique_targets):
                    mask = target_vals == t
                    color = colors[i] if target != "bbch" else colors.get(t, "gray")
                    self.ax.scatter(
                        principal_df.loc[mask, "PC1"],
                        principal_df.loc[mask, "PC2"],
                        c=[color],
                        label=str(t),
                        alpha=0.7,
                    )

                # Add legend
                self.ax.legend(title=f"{target} Groups")
            else:
                # Plot without grouping
                self.ax.scatter(
                    principal_df["PC1"], principal_df["PC2"], alpha=0.7, label="Data Points"
                )

            # Set labels and grid
            self.ax.set_xlabel("Principal Component 1")
            self.ax.set_ylabel("Principal Component 2")
            self.ax.set_title("PCA Visualization")
            self.ax.grid(True)

        except Exception as e:
            raise Exception(f"Error during PCA visualization: {str(e)}")