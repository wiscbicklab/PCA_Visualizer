import tkinter as tk
from tkinter import messagebox
import traceback
from matplotlib import cm, pyplot as plt
from matplotlib.colors import to_hex
from matplotlib.patches import Ellipse
import pandas as pd
import numpy as np
import seaborn as sns
import plotly.graph_objects as go

from scipy import stats

from source.gui.app_state  import AppState
import source.utils.file_operations as file_ops
from source.utils.constant import *

from adjustText import adjust_text


class CreatePlotBox(tk.Frame):
    """
    A GUI box for generating different types of plots using PCA analysis

    A banner with a header for the sections
    A label and check box for enabling group mapping
    A button for lading a mapping .csv file
    Two columns of buttons from left to right top to bottom:
        A button for creating and showing a Scree Plot
        A button for creating and showing a Biplot with Groups
        A button for creating and showing a Interactive Biplot
        A button for creating and showing a Top Feature Loadings Plot
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main, app_state: AppState, **kwargs):
        """
        Creats a space for Biplot generation buttons

        Args:
            main: tk.Widget
                The parent widget for this frame.
            app_state: AppState
                The app_state variable used to pass data between components
            **kwargs: dict
                Additional keyword arguments passed to tk.Frame.
        """
        # Intializes data about the container class
        super().__init__(main, **kwargs)
        self.app_state = app_state


        # Declares frame banner
        self.biplot_banner = None

        # Declares plot generation buttons
        self.pca_plot_bttn = None
        self.heatmap_mode_var = None # Variable For heatmap mode
        self.heatmap_bttn = None
        self.biplot_bttn = None
        self.interactive_biplot_bttn = None
        self.scree_plot_bttn = None
        self.top_feat_bttn = None


        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates frame banner
        self.biplot_banner = tk.Label(self, **BANNER_STYLE, text="Plot Generation")
        
        # Creates plot generation buttons
        self.pca_plot_bttn = tk.Button(self, text="Plot PCA", **BUTTON_STYLE, command=self.visualize_pca)
        self.heatmap_bttn = tk.Button(self, text="Plot Heatmap", **BUTTON_STYLE, command=self.create_heatmap_fig)
        self.scree_plot_bttn = tk.Button(self, text="Scree Plot", **BUTTON_STYLE, command=self.create_scree_plot)
        self.biplot_bttn = tk.Button(self, text="Biplot", **BUTTON_STYLE, command=self.create_biplot)
        self.interactive_biplot_bttn = tk.Button(self, text="Interactive Biplot", **BUTTON_STYLE, command=self.create_interactive_biplot)
        self.top_feat_bttn = tk.Button(self, text="Feature Loadings Plot", **BUTTON_STYLE, command=self.create_top_n_feat_plot)

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Places banner at the top of this component
        self.biplot_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Places plot generation buttons
        self.pca_plot_bttn.grid(row=1, column=0, padx=5, pady=5)
        self.heatmap_bttn.grid(row=1, column=1, padx=5, pady=5)
        self.biplot_bttn.grid(row=2, column=0, padx=5, pady=5)
        self.interactive_biplot_bttn.grid(row=2, column=1, padx=5, pady=5)
        self.scree_plot_bttn.grid(row=3, column=0, padx=5, pady=5)
        self.top_feat_bttn.grid(row=3, column=1, padx=5, pady=5)


    #### 1. Create PCA Visualization ####

    def visualize_pca(self):
        """
        Creates a PCA visualization based on the given inputs and updates GUI plot
        
        Creates a PCA plot of the first two prinicple components. Creates groupings using
            the selected Target Variable and gives them unique colors. Displays the generated plot.
        """
        # Validates that the data has been cleaned
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned in order to run PCA.")
            return  
        
        # Runs PCA Analysis and get important results
        self.app_state.main.run_analysis()
        transformed_data = self.app_state.pca_results['transformed_data']
        transformed_cols = [f'PC{i + 1}' for i in range(transformed_data.shape[1])]
        transformed_df = pd.DataFrame(transformed_data, columns=transformed_cols)
        
        # Gets the user selected target variable
        target = self.app_state.pca_target.get().strip()

        # Generate new blank figure
        self.app_state.main.create_blank_fig()
        # Adds title and axis lables to the figure
        self.app_state.ax.set_title("PCA Visualization")
        self.app_state.ax.set_xlabel("Principal Component 1")
        self.app_state.ax.set_ylabel("Principal Component 2")
        # Plot grouped by target if available
        if target in self.app_state.df.columns:
            # Gets the values for the given target
            target_vals = self.app_state.df[target].reset_index(drop=True)

            if target_vals.nunique() > 20:
                # Bin the values into 20 equal-width intervals
                binned = pd.cut(target_vals, bins=20, include_lowest=True)
                
                # Format the interval labels to show up to 6 significant digits
                def format_interval(interval):
                    left = f"{interval.left:.6g}"
                    right = f"{interval.right:.6g}"
                    return f"({left}, {right}]"

                formatted_bins = binned.apply(format_interval)
                target_vals = formatted_bins
                unique_targets = sorted(target_vals.unique())
            else:
                unique_targets = sorted(target_vals.unique())


            # Assign colors and add a legend
            colors = plt.cm.tab20(np.linspace(0, 1, len(unique_targets)))
            for i, t in enumerate(unique_targets):
                mask = target_vals == t
                color = colors[i]
                self.app_state.ax.scatter(
                    transformed_df.loc[mask, "PC1"],
                    transformed_df.loc[mask, "PC2"],
                    c=[color], label=str(t), alpha=0.7,
                )

            self.app_state.ax.legend(title=f"{target} Groups", bbox_to_anchor=(1.05, 1), loc='upper left')
            self.app_state.main.replace_status_text("PCA Plot Successfully Generated")
        else:
            # Plot without grouping
            self.app_state.ax.scatter(
                transformed_df["PC1"], transformed_df["PC2"], alpha=0.7, label="Data Points"
            )
            self.app_state.main.replace_status_text(f"{target} not found! Showing Default PCA Plot")


        self.app_state.main.update_figure()


    #### 2. Create Scree Plot ####

    def create_scree_plot(self):
        """Creates scree plot and puts it in the GUI"""
        # Validates required input data
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return

        # Ensures that pca analysis has been run
        self.app_state.main.run_analysis()
        
        # Creates a new blank figure without a grid
        self.app_state.main.create_blank_fig(grid=False)

        # Get the explained variance
        explained_variance = self.app_state.pca_results['explained_variance']

        try:
            # Adds a title and an x and y label
            self.app_state.ax.set_title('Scree Plot')
            self.app_state.ax.set_xlabel('Principal Component Index')
            self.app_state.ax.set_ylabel('Explained Variance Ratio')
            
            # Create a range for principal components
            pc_indices = range(1, len(explained_variance) + 1)

            # Creates bar plot of individual explained variance
            self.app_state.ax.bar(
                pc_indices,
                explained_variance,
                alpha=0.7,
                align='center'
            )
            
            # Creates step plot of cumulative explained variance
            self.app_state.ax.step(
                pc_indices,
                np.cumsum(explained_variance),
                where='mid',
                label='Cumulative explained variance'
            )

            # Set x-axis ticks to whole numbers only
            self.app_state.ax.set_xticks(pc_indices)
            
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred while generating the scree plot: {e}")
            return

        # Updates the figure on the GUI
        self.app_state.main.replace_status_text("Scree Plot Sucsessfully Generated")
        self.app_state.main.update_figure()


    #### 3. Create Biplot ####

    def create_biplot(self):
        """
        Creates a Biplot visualization based on the given inputs and updates GUI plot

        Creates a biplot using the Top N features selected by the user. Uses the top two
            priniciple components for the biplot. Creates a color map and addes it as a legend.
        """
        app_state = self.app_state
        if not app_state.df_cleaned:
            messagebox.showerror("Error", "DataFrame must be cleaned")
            return
        # Runs PCA analysis and gets relavent values
        scores, loadings, variance, eigvals, feat_names, top_idx, top_feat, __, num_feat = self.validate_biplot_data(app_state)

        # Intializes the figure
        if not self.init_biplot_fig(variance, num_feat, app_state): return 
        ax = app_state.ax

        # Add legend for groups
        try:
            color_map, user_mapping_enabled = self.get_color_mapping(top_feat, self.app_state)
            for group, color in color_map.items():
                label = group[:35] + ('...' if len(group) > 35 else '')
                ax.plot([], [], '-', color=color, label=label, linewidth=2)
            ax.legend(title="Groups", bbox_to_anchor=(1.05, 1), loc='upper left')
        except Exception as e:
            traceback.print_exc()
            return

        # Creates an elipse to represent confidence
        confidence_ellipse = stats.chi2.ppf(0.95, df=2)
        width = 2 * np.sqrt(eigvals[0] * confidence_ellipse)
        height = 2 * np.sqrt(eigvals[1] * confidence_ellipse)
        ellipse = Ellipse((0, 0), width=width, height=height, alpha=0.1, color='gray', linestyle='--')
        try:
            # Adds elipse to figure
            ax.add_patch(ellipse)

            # Sets axis limits
            variance_scale = np.sqrt(eigvals)
            scaled_loadings = loadings[:, :2] * variance_scale
            self.set_biplot_axis_limits(scaled_loadings, top_idx, ax)


            # Creates biplot arrows and arrow text
            self.add_biplot_arrows( top_idx, feat_names, scaled_loadings, color_map, ax)


            # Creates Scatter Plot
            ax.scatter(scores[:, 0], scores[:, 1], alpha=0.2, color='gray', s=30, label='Samples')
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occures while generating the biplot: {e}")
            return
        
        # Updates the figure on the GUI
        if user_mapping_enabled and app_state.feat_group_enabled:
            app_state.main.replace_status_text("No Feature Grouping Loaded! Generic Biplot Generated")
        else:
            app_state.main.replace_status_text("Biplot Sucsessfully Generated")

        self.app_state.main.update_figure()

    def init_biplot_fig(self, variance, num_feat, app_state: AppState):
        """
        Intializes a blank biplot with title and labels

        Args:
            varience: The variences explained by both of the PCA components
            num_feat: The number of top features to explaining the PCA components to show
        
        Returns:
            True if the initialization was successful and False if an exception occured
        """
        # Generates a new blank figure
        main = app_state.main
        main.create_blank_fig()        
        ax = app_state.ax
        
        try:
            # Adds title and labels to the figure
            ax.set_title(f"Biplot with Top {num_feat} Significant Features")
            ax.set_xlabel(f"PC1 ({variance[0]:.1%} explained var.)")
            ax.set_ylabel(f"PC2 ({variance[1]:.1%} explained var.)")

            # Set grid appearance and aspect ratio
            ax.grid(True, linestyle='--', alpha=0.3)
            ax.set_aspect('equal', adjustable='box')

            # Sets the background color of the plot
            ax.set_facecolor('#f8f9fa')
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def set_biplot_axis_limits(self, scaled_loadings, top_idx, ax):
        """
        Sets the figure axis limits for a biplot

        Args:
            scaled_loadings: Scaled PCA loadings sorted from greatest to smallest loading values
            top_idx:  The number of loadings to be used on the biplot
        """
        # Calulate the minimum and maximum x and y values from the scaled_loadings
        x_min, x_max = np.min(scaled_loadings[top_idx, 0]), np.max(scaled_loadings[top_idx, 0])
        y_min, y_max = np.min(scaled_loadings[top_idx, 1]), np.max(scaled_loadings[top_idx, 1])

        # Creates a margin based on the range of the x and y values
        margin = 0.2 * max(x_max - x_min, y_max - y_min)

        # Uses the x-y value range and margin to set the x and y axis limits
        ax.set_xlim(x_min - margin, x_max + margin)
        ax.set_ylim(y_min - margin, y_max + margin)

    def add_biplot_arrows(self, top_idx, feat_names, scaled_loadings, color_map, ax):
        """
        Adds arrows and arrow text to a biplot
        
        Args:
            top_feat:  List of the top PCA features
            top_idx:   List of the indexes of the top PCA features
            feat_names: List of all the PCA feature Names
            scaled_loadings:   List of all the PCA loadings
        """
        # Use the color mapping to add arrows to the plot
        for idx in top_idx:
            feature = feat_names[idx]
            
            # Get feature group and group color
            group = self.app_state.feat_group_map[feature]
            color = color_map.get(group)

            # Generate arrow
            ax.quiver(
                0, 0,
                scaled_loadings[idx, 0],
                scaled_loadings[idx, 1],
                angles='xy',
                scale_units='xy',
                scale=1,
                color=color,
                alpha=0.8,
                width=0.005,
                headwidth=3,
                headlength=5
            )


    #### 4. Create Interactive Biplot ####

    def create_interactive_biplot(self):
        """Creates an interactive biplot visualization and opens it in users webbrowser"""
        # Runs PCA analysis and gets relavent values
        __, loadings, variance, eigvals, feat_names, top_idx, top_feat, magnitudes, __ = self.validate_biplot_data(self.app_state)

        try:
            # Intializes figure
            fig = go.Figure()

            # Sets axis limits
            variance_scale = np.sqrt(eigvals)
            scaled_loadings = loadings[:, :2] * variance_scale
            self.add_interactive_biplot_groups(top_feat, top_idx, feat_names, scaled_loadings, magnitudes, fig)

            #Add interactivity to figure
            fig.update_layout(
                updatemenus=[{
                    "type": "buttons",
                    "buttons": [
                        dict(label="Show All Features",
                            method="update",
                            args=[{"visible": [True] * len(fig.data)}]),
                        dict(label="Show Top 10",
                            method="update",
                            args=[{"visible": [i < 10 for i in range(len(fig.data))]}]),
                    ],
                    "direction": "down",
                    "showactive": True,
                    "x": 0.1,
                    "y": 1.1,
                    "xanchor": "left",
                    "yanchor": "top"
                }],
            )
            fig.update_layout(
                title=f"Interactive Biplot with Top {self.app_state.num_feat.get()} Significant Features",
                xaxis_title=f"PC1 ({variance[0]:.1%} explained var.)",
                yaxis_title=f"PC2 ({variance[1]:.1%} explained var.)",
                clickmode='event+select',
                showlegend=True,
                legend=dict(
                    title="Feature Groups" if self.app_state.feat_group_map is not None else "Features",
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)"
                )
            )
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")
            return
        
        # Save plot, opens it in users browser, and shows success message
        file_name = file_ops.save_interactive_plot(fig, self.app_state.output_dir)
        if file_name is not None:
            self.app_state.main.replace_status_text("Interactive Biplot Sucsessfully Generated")
    def add_interactive_biplot_groups(self, top_feat, top_idx, feat_names, scaled_loadings, magnitudes, fig):
        """
        Adds biplot groupings to an interactive biplot

        Args:
            top_feat:  List of the top PCA features
            top_idx:   List of the indexes of the top PCA features
            feat_names: List of all the PCA feature Names
            scaled_loadings:   List of all the PCA loadings
            fig:    The figure to generate the biplot groupings on
        """
        # Gets the color mapping for the biplot
        color_map, user_mapping_enabled = self.get_color_mapping(top_feat, self.app_state)

        # Set for holding legend groups to avoid duplicate legend entries
        legend_groups = set()

        for idx in top_idx:
            feature = feat_names[idx]
            magnitude = magnitudes[idx]

            # Get feature color
            if self.app_state.feat_group_enabled.get():
                group = self.app_state.feat_group_map.get(feature)
                color = color_map.get(group)
            else:
                group = feature
                color = color_map.get(feature)

            # Only show legend for the group once; check if it's already been shown
            showlegend = group not in legend_groups
            legend_groups.add(group)

            # Add a vector (arrow) trace to the plot representing this feature's loadin
            fig.add_trace(go.Scatter(
                x=[0, scaled_loadings[idx, 0]],
                y=[0, scaled_loadings[idx, 1]],
                mode="lines+markers",
                line=dict(color=color, width=2),
                marker=dict(color=color),
                name=group if showlegend else feature,
                legendgroup=group,
                showlegend=showlegend,
                hovertext=(f"Feature: {feature}<br>"
                            f"Group: {group}<br>"
                            f"Loading PC1: {scaled_loadings[idx, 0]:.3f}<br>"
                            f"Loading PC2: {scaled_loadings[idx, 1]:.3f}<br>"
                            f"Magnitude: {magnitude:.3f}"),
                hoverinfo="text"
            ))
    

    #### 5. Create Top Feature Plot ####

    def create_top_n_feat_plot(self):
        """Creates a plot showing the top feature loadings of the selected PCA component and Update the GUI plot"""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return
        
        # Ensures PCA has been run
        self.app_state.main.run_analysis()

        # Get top N features from user input
        top_n = self.app_state.num_feat.get()
        pca_comp_num = self.app_state.focused_pca_num.get()-1

        # Intialize the plot
        if not self.init_top_feat_plot(top_n, pca_comp_num+1):
            messagebox.showerror("Error", "Error occured while attemping to initialize the new figure")
            return
        
        # Validate and retrieve loadings
        loadings = abs(self.app_state.pca_results['components'][pca_comp_num])
        feat_names = self.app_state.pca_results['feature_names']
        
        # Sorting the loadings
        sorted_pairs = sorted(zip(feat_names, loadings), key=lambda x: abs(x[1]), reverse=True)
        sorted_loadings, sorted_feat_names = zip(*sorted_pairs)
        sorted_loadings = list(sorted_loadings)
        sorted_feat_names = list(sorted_feat_names)
        
        try:
            # Plot top feature loadings
            self.app_state.ax.barh(
                sorted_loadings[:top_n],
                sorted_feat_names[:top_n],
                color='steelblue',
                alpha=0.8
            )
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"An error occurred while generating the top feature plot: {e}")
            return
        
        # Updates the figure on the GUI
        self.app_state.main.replace_status_text("Top Feature Plot Sucessfully Generated")
        self.app_state.main.update_figure()

    def init_top_feat_plot(self, top_n, pca_num):
        """
        Intializes a blank top feature plot with title and labels
        
        Args:
            top_n: The number of top features to show

        Returns:
            True if the initialization was successful and False if an exception occured
        """
        # Generates a new blank figure
        self.app_state.main.create_blank_fig(grid=False)
        try:
            # Adds title and labels to the figure
            self.app_state.ax.set_title(f"Top {top_n} Features - PCA{pca_num} Absolute Loadings", fontsize=14)
            self.app_state.ax.set_xlabel(f"PCA{pca_num} Absolute Loadings", fontsize=12)
            self.app_state.ax.set_ylabel("Features", fontsize=12)

            # Sets the x and y axis variable sizes and rotation, to ensure labels fit on plot
            self.app_state.ax.tick_params(axis='x', labelsize=10)
            self.app_state.ax.tick_params(axis='y', labelsize=10, rotation=45)
            return True
        except Exception as e:
            traceback.print_exc()
            return False
    
 
    #### 6. Data Functions ####

    def validate_biplot_data(self, app_state: AppState):
        """Runs PCA analysis and gets important pca results"""
        # Validates required input data
        if not app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            raise AttributeError("No data to Validate")

        # Ensure that PCA has been run and get results
        app_state.main.run_analysis()
        pca_results = app_state.pca_results
        
        # Grab important results
        scores = pca_results['transformed_data']
        loadings = pca_results['loadings']
        variance = pca_results['explained_variance']
        feat_names = [name.lower() for name in pca_results['feature_names']]

        # Calculate eigenvalues from results
        eigenvals = variance[:2]

        # Gets Users number of PCA results
        num_feat = app_state.num_feat.get()

        # Calculates PCA magnitudes and gets top indexes and features
        magnitudes = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_idx = np.argsort(magnitudes)[::-1][:num_feat]
        top_feat = app_state.df.columns[top_idx]

        return scores, loadings, variance, eigenvals, feat_names, top_idx, top_feat, magnitudes, num_feat
    
    def get_color_mapping(self, features, app_state: AppState):
        """
        Creates a color mapping for biplot groups or features

        Creates a color mapping using the selected color palette and extra generated colors
            when a feature group mapping is enabled has been uploaded. Creates a color mapping
            of the given features if using generated colors if feature group mapping is disabled.
        
        Args:
            top_feat: List of the top PCA features to color map
        
        Returns:
            feature mapping and feature colors

        Raises:
            Attribute Error: If feature grouping is enabled but a feature map hasn't been uploaded or
                    if feature gouping is disabled and no top_features are provided
            ValueError: If the number of features/groups without predefined colors is greater then 20
        """
        # Get User Selection
        grouping_enabled = app_state.feat_group_enabled.get()
        group_map = app_state.feat_group_map
        
        # Disable Grouping if no Group-Map is uploaded
        grouping_enabled = grouping_enabled and len(group_map) != 0

        # Find all unique groups in the features
        feat_groups = set()
        for feat in features:
            # Get the feature group from the group_map
            if grouping_enabled and feat in group_map.keys():
                feat_groups.add(group_map[feat])
            # Add the feature as a unique group to the group_map and add it to the feat_groups
            else:
                group_map[feat] = feat
                feat_groups.add(feat)

        # Gets the most appropriate color map
        if (len(feat_groups) > 20):
            messagebox.showerror("Mapping Error", f"{len(feat_groups)} groups without predfined colors where requested, but only 20 colors are available")
            raise ValueError("Mapping Error, not enough colors available for requested groups")  
        elif len(feat) > 10:
            colors = [to_hex(c) for c in plt.get_cmap('tab20').colors]
        else:
            colors = [to_hex(c) for c in plt.get_cmap('tab10').colors]
        
        # Map Groups to colors
        color_group_map = {}
        for group, color in zip(feat_groups, colors):
                color_group_map[group] = color
        
        return color_group_map, grouping_enabled
            
    


#### 2. VISUALIZATION METHODS ####

    def create_heatmap_fig(self):
        """
        Plot loadings heatmap using user-selected mode.
        
        Creates a heatmap using the top number of features selected or custom features.
            Shows the number of PCA components selected, and sorts the features by absolute 
            loadings of the selected PCA component to analize
        """
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return
        
        try:
            # Ensures PCA has been run
            self.app_state.main.run_analysis()

            # Creates a new blank figure
            self.app_state.main.create_blank_fig(grid=False)

            # Adds a title and x and y label 
            self.app_state.ax.set_title('Loadings Heatmap', fontsize=16)
            self.app_state.ax.set_xlabel('Principal Components', fontsize=14)
            self.app_state.ax.set_ylabel('Features', fontsize=14)

            # Sets tick parameters to fit on ax
            self.app_state.ax.tick_params(axis='x', labelsize=12)
            self.app_state.ax.tick_params(axis='y', labelsize=10)

            # Get user entered heatmap mode and PCA data
            loadings = abs(self.app_state.pca_results['loadings'])

            # Determine focus columns
            focus_columns = self.get_focus_cols(loadings)

            if focus_columns is None:
                return

            # Update the heatmap figure
            self.display_loadings_heatmap(
                loadings=loadings,
                data_columns=self.app_state.df.columns.tolist(),
                focus_columns=focus_columns,
                cmap="coolwarm"
            )

            # Ensure that the GUI updates
            self.app_state.main.replace_status_text("Heatmap Sucessfully Generated")
            self.app_state.main.update_figure()

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def get_focus_cols(self, loadings):
        """Determine columns to focus on based on heatmap mode."""
        try:
            # Get the column and loadings data
            df_cols = self.app_state.df.columns.tolist()

            # Get absolute loadings for the first principal component
            pc1_loadings = abs(loadings[:, self.app_state.focused_pca_num.get()-1])
            loading_series = pd.Series(pc1_loadings, index=df_cols)
            sorted_columns = loading_series.sort_values(ascending=False).index.tolist()
            
            # Get the users heatmap targets
            target_feats = set([feat.strip() for feat in  self.app_state.heatmap_feat.get().strip().split(',') if feat.strip()])

            # Returns the top Features if the target is empty
            if not target_feats:
                return sorted_columns[:self.app_state.num_feat.get()]
            else:
                # Gets the focused columns and missing columns
                df_feats = set(self.app_state.df.columns)
                focus_feats = target_feats & df_feats
                missing_feat = target_feats - focus_feats

                # If there are missing features, infom the user by updating the status
                if len(missing_feat) != 0:
                    self.app_state.main.replace_status_text(f"Heatmap Failed! Selected Features Not Found In Data!")
                    self.app_state.main.replace_pca_text(f"Missing Features:\t{[feat for feat in missing_feat]}")
                
                return_list = [feat for feat in focus_feats]

            return return_list or None
        except Exception as e:
            messagebox.showerror("Error", f"Error determining focus columns: {str(e)}")
            return None

    def display_loadings_heatmap(self, loadings, data_columns, focus_columns=None, cmap='viridis'):
        """
        Display a heatmap of loadings with improved design.

        Args:
            loadings: PCA loadings matrix.
            data_columns: List of all data column names.
            focus_columns: List of columns to focus on. Defaults to None.
            cmap: Colormap to use for the heatmap.
        """
        if focus_columns is None:
            focus_columns = data_columns  # Default to all columns if none specified

        # Select only the relevant rows from the loadings matrix
        selected_loadings = loadings[[data_columns.index(col) for col in focus_columns], :]

        # Create the heatmap
        plt.figure(self.app_state.fig_size[0])  # Increase figure size for clarity
        sns.heatmap(
            selected_loadings,
            annot=True,  # Add annotations to cells
            fmt=".2f",  # Format numbers
            cmap=cmap,  # Use perceptually uniform colormap
            cbar_kws={'label': 'Absolute Loadings'},  # Single, descriptive colorbar
            xticklabels=[f'PC{i + 1}' for i in range(loadings.shape[1])],
            yticklabels=focus_columns,
            ax=self.app_state.ax
        )

        # Adds a title and x and y label
        self.app_state.ax.set_title('Loadings Heatmap', fontsize=16)
        self.app_state.ax.set_xlabel('Principal Components', fontsize=14)
        self.app_state.ax.set_ylabel('Features', fontsize=14)
        # Sets axis lablel size
        self.app_state.ax.tick_params(axis='x', labelsize=12)
        self.app_state.ax.tick_params(axis='y', labelsize=10)


