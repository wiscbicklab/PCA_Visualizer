import os
import time
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
from matplotlib import cm
from matplotlib.colors import to_hex
from matplotlib.patches import Ellipse
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io


from scipy import stats

from source.gui.app_state  import AppState

from adjustText import adjust_text


from source.utils.constant import *

import source.utils.file_operations as file_ops


class BiplotBox(tk.Frame):
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

    #### 0. Setup GUI Elements ####

    def __init__(self, main, app_state: AppState, **kwargs):
        """Initializes box for cleaning user data"""
        # Intializes data about the container class
        super().__init__(main, **kwargs)
        self.app_state = app_state

        # Declares frame banner
        self.biplot_banner = None

        # Declares feature mapping components
        self.grouping_checkbox = None
        self.mapping_label = None
        self.mapping_button = None

        # Declares plot generation buttons
        self.biplot_button = None
        self.interactive_biplot_button = None
        self.scree_plot_button = None
        self.top_features_button = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()

    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates frame banner
        self.biplot_banner = tk.Label(self, **BANNER_STYLE, text="Biplot Section")
        
        # Creates feature mapping components
        self.grouping_checkbox = tk.Checkbutton(
            self,
            text="Enable Feature Grouping",
            variable=self.app_state.feat_group_enable,
            **LABEL_STYLE,
            command=self.toggle_feature_grouping
        )
        self.mapping_label = tk.Label(self, **LABEL_STYLE, text="Feature-to-Group Mapping (Optional):")
        self.mapping_button = tk.Button(self, text="Upload Mapping CSV", **BUTTON_STYLE, command=self.upload_mapping)
        self.mapping_button.config(state="normal")

        # Creates plot generation buttons
        self.biplot_button = tk.Button(self, text="Biplot with Groups", **BUTTON_STYLE, command=self.create_biplot)
        self.interactive_biplot_button = tk.Button(self, text="Interactive Biplot", **BUTTON_STYLE, command=self.create_interactive_biplot)
        self.scree_plot_button = tk.Button(self, text="Show Scree Plot", **BUTTON_STYLE, command=self.create_scree_plot)
        self.top_features_button = tk.Button(self, text="Top Features Loadings", **BUTTON_STYLE, command=self.create_top_n_feat_plot)

    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Places banner at the top of this component
        self.biplot_banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Places feature grouping components
        self.grouping_checkbox.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.mapping_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.mapping_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Places plot generation buttons
        self.scree_plot_button.grid(row=3, column=0, padx=5, pady=5)
        self.biplot_button.grid(row=3, column=1, padx=5, pady=5)
        self.interactive_biplot_button.grid(row=4, column=0, padx=5, pady=5)
        self.top_features_button.grid(row=4, column=1, padx=5, pady=5)


    #### 1. Create Plots ####

    def create_scree_plot(self):
        """Creates scree plot and puts it in the GUI"""
        # Validates required input data
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return

        # Intializes the figure
        if not self.init_scree_fig(): return
        
        # Get the explained variance
        __, __, explained_variance, __, __ = self.get_pca_data()

        try:
            # Creates bar plot of individual explained variance
            self.app_state.ax.bar(
                range(1, len(explained_variance) + 1),
                explained_variance,
                alpha=0.7,
                align='center'
            )
            # Creates step plot of cumulative explained variance
            self.app_state.ax.step(
            range(1, len(explained_variance) + 1),
            np.cumsum(explained_variance),
            where='mid',
            label='Cumulative explained variance'
        )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the scree plot: {e}")
            return

        # Updates the figure on the GUI
        self.app_state.main.update_figure()

    def create_biplot(self):
        """Creates biplot visualization and puts it in the GUI"""
        # Validates required input data
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return False
        if self.app_state.feat_group_enable.get() and self.app_state.feat_map is None:
            messagebox.showerror("Error", "Feature Groups is enabled, but a feature group has not been uploaded!")
            return False

        # Runs PCA analysis and gets relavent values
        scores, loadings, variance, eigenvals, feat_names = self.get_pca_data()
        # Calculates other need information based on the PCA Resulats
        top_idx, loading_magnitudes, num_feat = self.get_top_pca_features(loadings)
        top_feat = self.app_state.df.columns[top_idx]

        # Intializes the figure
        if not self.init_biplot_fig(variance, num_feat): return 

        # Add legend for groups
        feat_map, feat_colors = self.get_color_mapping(top_feat)
        for group, color in feat_colors.items():
            self.app_state.ax.plot([], [], '-', color=color, label=group, linewidth=2)
        self.app_state.ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # Creates an elipse to represent confidence
        confidence_ellipse = stats.chi2.ppf(0.95, df=2)
        width = 2 * np.sqrt(eigenvals[0] * confidence_ellipse)
        height = 2 * np.sqrt(eigenvals[1] * confidence_ellipse)
        ellipse = Ellipse((0, 0), width=width, height=height, alpha=0.1, color='gray', linestyle='--')
        try:
            # Adds elipse to figure
            self.app_state.ax.add_patch(ellipse)
            # Sets axis limits
            variance_scale = np.sqrt(eigenvals)
            scaled_loadings = loadings[:, :2] * variance_scale
            self.set_biplot_axis_limits(scaled_loadings, top_idx)

            # Creates biplot arrows and arrow text
            self.add_biplot_arrows(top_feat, top_idx, feat_names, loading_magnitudes, scaled_loadings)

            # Creates Scatter Plot
            self.app_state.ax.scatter(scores[:, 0], scores[:, 1], alpha=0.2, color='gray', s=30, label='Samples')
        except Exception as e:
            messagebox.showerror("Error", f"An error occures while generating the biplot: {e}")
            return
        
        # Updates the figure on the GUI
        self.app_state.main.update_figure()

    def create_interactive_biplot(self):
        """Creates an interactive biplot visualization and opens it in users webbrowser"""
        # Validates required input data
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return False
        if self.app_state.feat_group_enable.get() and self.app_state.feat_map is None:
            messagebox.showerror("Error", "Feature Groups is enabled, but a feature group has not been uploaded!")
            return False
        
        # Runs PCA analysis and gets relavent values
        __, loadings, variance, eigenvals, feat_names = self.get_pca_data()
        # Calculates other need information based on the PCA Resulats
        top_idx, loading_magnitudes, __ = self.get_top_pca_features(loadings)
        top_feat = self.app_state.df.columns[top_idx]

        try:
            # Intializes figure
            fig = go.Figure()

            # Sets axis limits
            variance_scale = np.sqrt(eigenvals)
            scaled_loadings = loadings[:, :2] * variance_scale
            self.add_interactive_biplot_groups(top_feat, top_idx, feat_names, loading_magnitudes, scaled_loadings, fig)

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
                sliders=[{
                    "steps": [
                        dict(
                            method="update",
                            args=[{"visible": [abs(loading_magnitudes[i]) > t for i in range(len(top_idx))]}],
                            label=f"{t:.1f}"
                        ) for t in np.linspace(0, 1, 10)
                    ],
                    "currentvalue": {"prefix": "Significance Threshold: "}
                }]
            )
            fig.update_layout(
                title=f"Interactive Biplot with Top {self.app_state.top_n_feat.get()} Significant Features",
                xaxis_title=f"PC1 ({variance[0]:.1%} explained var.)",
                yaxis_title=f"PC2 ({variance[1]:.1%} explained var.)",
                clickmode='event+select',
                showlegend=True,
                legend=dict(
                    title="Feature Groups" if self.app_state.feat_map is not None else "Features",
                    yanchor="top",
                    y=0.99,
                    xanchor="right",
                    x=0.99,
                    bgcolor="rgba(255, 255, 255, 0.8)"
                )
            )
        except Exception as e:
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")
            return
        
        # Save plot, opens it in users browser, and shows success message
        file_name = self.save_interactive_plot(fig)
        if file_name is not None:
            messagebox.showinfo("Sucess", f"Interactive pca plot sucessfully created: {file_name}")

    def create_top_n_feat_plot(self):
        """Creates a plot showing the top feature loadings of the selected PCA component and puts it on the GUI"""
        if not self.app_state.df_cleaned.get():
            messagebox.showerror("Error", "Data must be cleaned first!")
            return
        
        # Ensures PCA has been run
        self.app_state.main.run_analysis()

        # Get top N features from user input
        top_n = self.app_state.top_n_feat.get()
        pca_comp_num = self.app_state.pca_num.get()-1

        # Intialize the plot
        if not self.init_top_feat_plot(top_n):
            messagebox("Error", "Error occured while attemping to initialize the new figure")
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
            messagebox.showerror("Error", f"An error occurred while generating the top feature plot: {e}")
            return
        
        # Updates the figure on the GUI
        self.app_state.main.update_figure()
        messagebox.showinfo("Success", f"Top {top_n} feature loadings plotted successfully!")


    #### 2. Figure Intialization ####

    def init_scree_fig(self):
        """
        Intializes a blank scree plot with title and labels
        
        Returns:
            True if the initialization was successful and False if an exception occured
        """
        # Generates a new blank figure
        self.app_state.main.create_blank_fig(grid=False)
        try:
            # Adds title and labels to the figure
            self.app_state.ax.set_title('Scree Plot')
            self.app_state.ax.set_xlabel('Principal Component Index')
            self.app_state.ax.set_ylabel('Explained Variance Ratio')
            return True
        except Exception as e:
            return False
            
    def init_biplot_fig(self, variance, num_feat):
        """
        Intializes a blank biplot with title and labels

        Args:
            varience: The variences explained by both of the PCA components
            num_feat: The number of top features to explaining the PCA components to show
        
        Returns:
            True if the initialization was successful and False if an exception occured
        """
        # Generates a new blank figure
        self.app_state.main.create_blank_fig()
        try:
            # Adds title and labels to the figure
            self.app_state.ax.set_title(f"Biplot with Top {num_feat} Significant Features")
            self.app_state.ax.set_xlabel(f"PC1 ({variance[0]:.1%} explained var.)")
            self.app_state.ax.set_ylabel(f"PC2 ({variance[1]:.1%} explained var.)")

            # Set grid appearance and aspect ratio
            self.app_state.ax.grid(True, linestyle='--', alpha=0.3)
            self.app_state.ax.set_aspect('equal', adjustable='box')

            # Sets the background color of the plot
            self.app_state.ax.set_facecolor('#f8f9fa')
            return True
        except Exception as e:
            return False

    def init_top_feat_plot(self, top_n):
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
            self.app_state.ax.set_title(f"Top {top_n} Features - Absolute Loadings", fontsize=14)
            self.app_state.ax.set_xlabel("Absolute Loadings", fontsize=12)
            self.app_state.ax.set_ylabel("Features", fontsize=12)

            # Sets the x and y axis variable sizes and rotation, to ensure labels fit on plot
            self.app_state.ax.tick_params(axis='x', labelsize=10)
            self.app_state.ax.tick_params(axis='y', labelsize=10, rotation=45)
            return True
        except Exception as e:
            return False


    #### 3. Figure Layout ####

    def set_biplot_axis_limits(self, scaled_loadings, top_idx):
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
        self.app_state.ax.set_xlim(x_min - margin, x_max + margin)
        self.app_state.ax.set_ylim(y_min - margin, y_max + margin)
#TODO: Check this docstring/implementation
    def add_biplot_arrows(self, top_feat, top_idx, feat_names, magnitudes, scaled_loadings):
        """
        Adds arrows and arrow text to a biplot
        
        Args:
            top_feat:  List of the top PCA features
            top_idx:   List of the indexes of the top PCA features
            feat_names: List of all the PCA feature Names
            magnitudes: List of all the PCA feature magnitudes
            scaled_loadings:   List of all the PCA loadings
        """
        # List for holding generated text objects for the plot
        texts = []

        # Gets the color mapping for the biplot
        feat_map, feat_colors = self.get_color_mapping(top_feat)

        # Use the color mapping to add arrows to the plot
        for idx in top_idx:
            feature = feat_names[idx]
            magnitude = magnitudes[idx]

            # Skip if magnitude isn't large enough
            if magnitude < 0.2:
                continue
            
            # Get feature grouping and color
            group = feat_map.get(feature)
            color = feat_colors.get(group)

            # Generate arrow
            self.app_state.ax.quiver(
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
            
            # Gets text distance from user Entry
            text_dist = self.app_state.text_dist.get()

            # Generates text for the plot and adds it to the list of texts
            text = self.app_state.ax.text(
                scaled_loadings[idx, 0] * text_dist,
                scaled_loadings[idx, 1] * text_dist,
                feature,
                fontsize=10,
                color=color,
                ha='center',
                va='center'
            )
            texts.append(text)

        # Settings to control the text around arrows on the plot?
        adjust_text(
            texts,
            arrowprops=dict(
                arrowstyle='->',
                color='gray',
                alpha=0.5,
                lw=0.5,
                shrinkA=10,  # Moves arrowhead away from text
                shrinkB=10  # Moves arrow tail away from origin
            ),
            force_text=1.5,  # Increased repulsion force to avoid overlaps
            force_points=0.8,  # Avoid overlapping with points
            expand_text=(1.5, 1.5),  # More spacing between labels
            expand_points=(1.2, 1.2),  # Ensure spacing from points
            lim=500  # Higher limit for iterations if overlaps persist
        )

    def add_interactive_biplot_groups(self, top_feat, top_idx, feat_names, magnitudes, scaled_loadings, fig):
        """
        Adds biplot groupings to an interactive biplot

        Args:
            top_feat:  List of the top PCA features
            top_idx:   List of the indexes of the top PCA features
            feat_names: List of all the PCA feature Names
            magnitudes: List of all the PCA feature magnitudes
            scaled_loadings:   List of all the PCA loadings
            fig:    The figure to generate the biplot groupings on
        """
        # Gets the color mapping for the biplot
        feat_map, feat_colors = self.get_color_mapping(top_feat)

        # Set for holding legend groups to avoid duplicate legend entries
        legend_groups = set()

        for idx in top_idx:
            feature = feat_names[idx]
            magnitude = magnitudes[idx]

            # Skip if magnitude isn't large enough
            if magnitude < 0.2:
                continue

            # Get the group this feature belongs to and its corresponding color
            group = feat_map.get(feature)
            color = feat_colors.get(group)

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

 
    #### 4. Data Functions ####

    def get_pca_data(self):
        """Runs PCA analysis and gets important pca results"""
        # Ensure that PCA has been run and get results
        self.app_state.main.run_analysis()
        pca_results = self.app_state.pca_results
        
        # Grab important results
        scores = pca_results['transformed_data']
        loadings = pca_results['loadings']
        variance = pca_results['explained_variance']
        feat_names = [name.lower() for name in pca_results['feature_names']]

        # Calculate eigenvalues from results
        eigenvals = variance[:2]

        return scores, loadings, variance, eigenvals, feat_names
    
    def get_top_pca_features(self, loadings):
        """Gets the top results of PCA analysis based on user selected input"""
        # Gets Users number of PCA results
        num_feat = self.app_state.top_n_feat.get()

        # Calculates PCA magnitudes and related component indexes
        magnitudes = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_idx = np.argsort(magnitudes)[::-1][:num_feat]

        return top_idx, magnitudes, num_feat
    
    def get_color_mapping(self, top_feat):
        """
        Gets the user uploaded color mapping or creates one otherwise
        
        Args:
            top_feat: List of the top PCA features to color map
        
        Returns:
            feature mapping and feature colors
        """
        # Generates a generic color mapping if one hasn't been uploaded
        if self.app_state.feat_map is None or len(self.app_state.feat_map) != self.app_state.top_n_feat.get():
            colormap = cm.get_cmap('tab20', len(top_feat))
            self.app_state.feat_map = {feature.lower(): feature for feature in top_feat}
            self.app_state.feat_colors = {
                feature: to_hex(colormap(i)) for i, feature in enumerate(top_feat)
            }
        print(self.app_state.feat_map)
        print(self.app_state.feat_colors)
        # Returns the existing color mapping or the generated one
        return self.app_state.feat_map, self.app_state.feat_colors


    #### 5. Save Interactive Plot ####

    def save_interactive_plot(self, fig):
        """
        Save an interactive biplot figure as an html file and opens it in the users browser

        Args:
            fig: Is the biplot figure to be saved and opened
        
        Returns:
            The filename of the saved figure or None if the file failed to save or open
        """

        output_dir = self.app_state.output_dir
        # Creates the output path if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Create file name and save_path
        time_stamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"Interactive_Biplot_{time_stamp}.html"
        save_path = os.path.join(self.app_state.output_dir, filename)
        config = {
            'scrollZoom': True,
            'displayModeBar': True,
            'editable': True
        }
        try:
            # Save the figure to the file save path
            plotly.io.write_html(fig, file=save_path, config=config)

            # Open the file in the users webrowser
            webbrowser.open(f'file://{os.path.abspath(save_path)}')
        except Exception as e:
            messagebox.showerror(
                "File Error",
                f"An error occured attempting to save and open the interactive biplot.\t{e}"
            )
            return None

        return filename


    #### 6. Feature Grouping Operations ####

#TODO: Add checks to ensure the csv contents are valid for this process
    def upload_mapping(self):
        """Allow the user to upload a mapping CSV file for feature-to-group mapping."""
        # Asks the user to select a csv file and ensures one was selected
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            messagebox.showerror("Error", "No file selected. Please upload a valid mapping CSV.")
            return
        
        # Ensures that the user selected a CSV file
        if not file_path.lower().endswith(".csv"):
            messagebox.showerror(
                "File Error",
                f"The selected file: {file_path} is not a csv file. You must select a CSV file")

        try:
            # Load the CSV into a DataFrame
            df = pd.read_csv(file_path)

            # Validate input DataFrame
            if 'Feature' not in df.columns.to_list() or 'Group' not in df.columns.to_list():
                messagebox.showerror("Error", "Invalid Feature File, 'Feature' or 'Group' column not found")
                return

            # Create feature-to-group mapping and standardize to lowercase
            self.app_state.feat_map = {
                key.lower(): value for key, value in zip(df['Feature'], df['Group'])
            }

            # Get unique groups
            unique_groups = sorted(df['Group'].unique())

            # Generate a dynamic color palette for groups
            colormap = cm.get_cmap('tab20', len(unique_groups))  # Use a colormap with sufficient distinct colors
            self.app_state.feat_colors = {
                group: to_hex(colormap(i)) for i, group in enumerate(unique_groups)
            }

            messagebox.showinfo("Success", "Feature-to-Group mapping loaded successfully.")
        
        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")

    def toggle_feature_grouping(self):
        """Toggle the feature grouping functionality."""
        if self.app_state.feat_group_enable.get():
            # Enable the mapping upload button
            self.mapping_button.config(state="normal")
            messagebox.showinfo("Feature Grouping Enabled",
                                "Feature grouping is now enabled. Please upload a mapping file.")
        else:
            # Disable the mapping upload button and reset group-related variables
            self.app_state.feat_map = None
            self.app_state.feat_colors = None

            # Clear results or mapping display
            if hasattr(self, 'feature_results_summary') and self.feature_results_summary is not None:
                self.feature_results_summary.config(state="normal")
                self.feature_results_summary.delete(1.0, tk.END)
                self.feature_results_summary.config(state="disabled")

            messagebox.showinfo("Feature Grouping Disabled", "Feature grouping has been disabled.")



