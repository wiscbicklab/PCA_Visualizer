import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from source.visualization.base import BasePlotter
from source.visualization.pca_visualization import PCAVisualizer
from source.visualization.biplot import BiplotVisualizer
from source.visualization.scree import ScreePlotVisualizer
from source.visualization.heatmap import LoadingsHeatmapVisualizer
from source.visualization.loadings import LoadingsProcessor

from source.analysis.pca import PCAAnalyzer

from source.utils.constant import OUTPUT_DIR, FEATURE_GROUPS_COLORS, DEFAULT_COLUMNS_TO_DROP
from source.utils.file_operations import load_file, save_plot
from source.utils.helpers import generate_color_palette
import time
import os


class PCAAnalysisApp:
    def __init__(self, master):
        self.master = master
        self.pca_analyzer = PCAAnalyzer()

        # Configure the master window
        master.title("PCA Analysis Tool")
        master.geometry("1200x800")
        master.configure(bg="#f5f5f5")
        master.minsize(1000, 600)

        # Define style constants
        self.button_style = {
            'font': ('Helvetica', 10),
            'bg': '#007ACC',
            'fg': 'white',
            'activebackground': '#005f99',
            'relief': 'raised',
            'width': 18
        }

        # Initialize variables
        self.target_var = tk.StringVar(value="None")
        self.missing_choice = tk.StringVar(value="impute_mean")
        self.bbch_choice = tk.IntVar(value=-1)
        self.enable_feature_grouping = tk.BooleanVar(value=False)
        self.heatmap_mode = tk.StringVar(value="Top 10 Features")
        self.target_mode = tk.StringVar(value="Select Target")
        self.feature_to_group = None
        self.scaler = StandardScaler()
        self.pca = None
        self.cleaned_data = None
        self.standardized_data = None
        self.data = None

        # Create the matplotlib figure
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)

        # Initialize all widgets
        self.create_widgets()

        # Set up the layout
        self.setup_layout()

        # Initially disable visualization buttons
        self.disable_visualization_buttons()



    def disable_visualization_buttons(self):
        """Disable all visualization buttons"""
        for button in [self.visualize_button, self.biplot_button,
                       self.interactive_biplot_button,
                       self.scree_plot_button, self.top_features_button,
                       self.save_button]:
            button.config(state="disabled")

    def enable_visualization_buttons(self):
        """Enable visualization buttons after successful PCA."""
        self.visualize_button.config(state="normal")
        self.biplot_button.config(state="normal")
        self.interactive_biplot_button.config(state="normal")
        self.heatmap_button.config(state="normal")
        self.scree_plot_button.config(state="normal")
        self.top_features_button.config(state="normal")
        self.save_button.config(state="normal")

        #### 1. CORE DATA HANDLING METHODS ####

    def clean_data(self):
        """Clean and prepare data for analysis."""
        if not self.validate_data_exists():
            return

        try:
            clean_options = {
                'missing_strategy': self.missing_choice.get(),
                'bbch_filter': self.bbch_choice.get(),
                'drop_columns': self.get_columns_to_drop()
            }

            self.data = self.pca_analyzer.clean_data(
                data=self.data,
                **clean_options
            )

            messagebox.showinfo("Success", "Data cleaned successfully!")
            self.update_data_info()

        except Exception as e:
            messagebox.showerror("Error", f"Data cleaning failed: {str(e)}")



        #### 2. UTILITY METHODS ####
    def get_columns_to_drop(self):
        """Get list of columns to drop, checking for existence first."""
        user_columns = [col.strip() for col in self.drop_entry.get().split(",") if col.strip()]
        all_columns = list(set(user_columns + DEFAULT_COLUMNS_TO_DROP))

        if hasattr(self, 'data') and self.data is not None:
            existing_columns = [col for col in all_columns if col in self.data.columns]
            if len(existing_columns) != len(all_columns):
                missing_columns = set(all_columns) - set(existing_columns)
                print(f"Warning: Some columns were not found in the dataset: {missing_columns}")
            return existing_columns
        return all_columns

    def update_data_info(self):
        """Update display with current data information."""
        if hasattr(self, 'data') and self.data is not None:
            info_text = f"Loaded data shape: {self.data.shape}\n"
            info_text += f"Columns: {', '.join(self.data.columns[:5])}..."
            self.pcaresults_summary.delete(1.0, tk.END)
            self.pcaresults_summary.insert(tk.END, info_text)

    def update_results_display(self, results):
        """Update results text displays."""
        self.pcaresults_summary.delete(1.0, tk.END)
        summary = f"PCA Analysis Results:\n\n"
        summary += f"Number of components: {results['n_components']}\n"
        summary += f"Original data shape: {results['original_shape']}\n"
        summary += f"Prepared data shape: {results['prepared_shape']}\n"

        explained_var = results['explained_variance']
        summary += "\nExplained Variance Ratios:\n"
        for i, var in enumerate(explained_var):
            summary += f"PC{i + 1}: {var:.3f}\n"

        self.pcaresults_summary.insert(tk.END, summary)

    #### 2. VISUALIZATION METHODS ####

    def visualize_pca(self):
        """Visualize PCA results using the visualizer."""
        try:
            pca_visualizer = PCAVisualizer(self.fig, self.ax)
            principal_components = self.pca_model.transform(self.x_standardized)

            target_mode = self.target_mode.get()
            target = "BBCH" if target_mode == "BBCH" else (
                self.custom_target_entry.get().strip() if target_mode == "Input Specific Target" else None
            )

            pca_visualizer.plot(
                principal_components=principal_components,
                data=self.data,
                target=target,
                target_mode=target_mode
            )
            self.update_figure()
        except Exception as e:
            messagebox.showerror("Visualization Error", str(e))

    def create_scree_plot(self):
        """Create scree plot using visualizer."""
        try:
            scree_visualizer = ScreePlotVisualizer(self.fig, self.ax)
            scree_visualizer.create_scree_plot(self.pca_model)
            self.update_figure()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating scree plot: {str(e)}")

    def create_biplot(self, significance_threshold=0.2):
        """Create biplot using the visualizer."""
        try:
            biplot_visualizer = BiplotVisualizer(self.fig, self.ax)
            biplot_visualizer.create_biplot(
                pca_model=self.pca_model,
                x_standardized=self.x_standardized,
                data=self.data,
                feature_to_group=self.feature_to_group,
                feature_groups_colors=self.feature_groups_colors,
                text_distance=float(self.text_distance_entry.get()),
                top_n=int(self.top_n_entry.get()),
                enable_feature_grouping=self.enable_feature_grouping.get(),
                significance_threshold=significance_threshold
            )
            self.update_figure()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating biplot: {str(e)}")

    def create_interactive_biplot(self, significance_threshold=0.2):
        """Create interactive biplot using plotly."""
        try:
            biplot_visualizer = BiplotVisualizer(self.fig, self.ax)
            fig = biplot_visualizer.create_interactive_biplot(
                pca_model=self.pca_model,
                x_standardized=self.x_standardized,
                data=self.data,
                text_distance=float(self.text_distance_entry.get()),
                top_n=int(self.top_n_entry.get()),
                feature_grouping=self.enable_feature_grouping.get(),
                feature_to_group=self.feature_to_group
            )

            save_path = save_plot(fig, "Interactive_Biplot")
            messagebox.showinfo("Interactive Biplot Saved", f"Interactive Biplot saved at {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating interactive biplot: {str(e)}")

    def display_loadings_heatmap(self):
        """Display loadings heatmap using visualizer."""
        try:
            heatmap_visualizer = LoadingsHeatmapVisualizer(self.fig, self.ax)
            heatmap_visualizer.display_loadings_heatmap(
                pca_model=self.pca_model,
                data=self.data,
                heatmap_mode=self.heatmap_mode.get(),
                focus_entry=self.focus_entry.get() if self.heatmap_mode.get() == "Custom Features" else None
            )
            self.update_figure()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating heatmap: {str(e)}")

    def plot_top_features_loadings(self):
        """Plot top features loadings using LoadingsProcessor."""
        try:
            loadings_processor = LoadingsProcessor(self.pca_model, self.data)
            loadings_processor.plot_top_features(
                fig=self.fig,
                ax=self.ax,
                top_n=int(self.top_n_entry.get())
            )
            self.update_figure()
        except Exception as e:
            messagebox.showerror("Error", f"Error plotting top features: {str(e)}")

    #### 3. EVENT HANDLERS ####

    def handle_successful_load(self, file_path):
        """Handle successful file load."""
        messagebox.showinfo("Success", f"File loaded successfully: {file_path}")
        self.clean_data_button.config(state="normal")
        self.run_button.config(state="normal")
        self.update_data_info()

    def handle_load_error(self, error):
        """Handle file loading errors."""
        messagebox.showerror("Error", f"Failed to load file: {str(error)}")

    def handle_analysis_results(self, results):
        """Handle successful PCA analysis results."""
        try:
            self.pca_model = results['model']
            self.x_standardized = results['standardized_data']
            self.update_results_display(results)
            self.enable_visualization_buttons()
            messagebox.showinfo("Success", "PCA analysis completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Error processing results: {str(e)}")

    def handle_analysis_error(self, error):
        """Handle PCA analysis errors."""
        messagebox.showerror("Error", f"PCA analysis failed: {str(error)}")

    def handle_successful_cleaning(self):
        """Handle successful data cleaning."""
        messagebox.showinfo("Success", "Data cleaned successfully!")
        self.update_data_info()

    def handle_cleaning_error(self, error):
        """Handle data cleaning errors."""
        messagebox.showerror("Error", f"Data cleaning failed: {str(error)}")

    #### 4. WIDGET STATE METHODS ####

    def update_target_input(self, *args):
        """Handle target input mode changes."""
        if self.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.delete(0, tk.END)
            self.custom_target_entry.config(state="disabled")

    def toggle_feature_grouping(self):
        """Enable or disable the mapping upload button based on checkbox state."""
        if self.enable_feature_grouping.get():
            self.mapping_button.config(state="normal")
            # Disable grouping-dependent buttons until mapping is uploaded
            self.biplot_button.config(state="disabled")
            self.interactive_biplot_button.config(state="disabled")
        else:
            self.mapping_button.config(state="disabled")
            # Re-enable grouping-dependent buttons if PCA has been run
            if hasattr(self, 'pca_model') and self.pca_model is not None:
                self.biplot_button.config(state="normal")
                self.interactive_biplot_button.config(state="normal")
            self.feature_to_group = None
            # Clear the feature mapping display
            self.featureresults_summary.config(state="normal")
            self.featureresults_summary.delete(1.0, tk.END)
            self.featureresults_summary.config(state="disabled")


    def enable_visualization_buttons(self):
        """Enable visualization buttons after successful analysis."""
        for button in [self.visualize_button, self.biplot_button,
                       self.interactive_biplot_button, self.heatmap_button,
                       self.scree_plot_button, self.top_features_button,
                       self.save_button]:
            button.config(state="normal")

    def disable_visualization_buttons(self):
        """Disable visualization buttons."""
        for button in [self.visualize_button, self.biplot_button,
                       self.interactive_biplot_button, self.heatmap_button,
                       self.scree_plot_button, self.top_features_button,
                       self.save_button]:
            button.config(state="disabled")

    #### 5. DISPLAY UPDATE METHODS ####

    def update_data_info(self):
        """Update display with current data information."""
        if hasattr(self, 'data') and self.data is not None:
            info_text = f"Loaded data shape: {self.data.shape}\n"
            info_text += f"Columns: {', '.join(self.data.columns[:5])}..."
            self.pcaresults_summary.delete(1.0, tk.END)
            self.pcaresults_summary.insert(tk.END, info_text)

    def update_results_display(self, results):
        """Update results text displays."""
        self.pcaresults_summary.delete(1.0, tk.END)
        summary = f"PCA Analysis Results:\n\n"
        summary += f"Number of components: {results['n_components']}\n"
        summary += f"Original data shape: {results['original_shape']}\n"
        summary += f"Prepared data shape: {results['prepared_shape']}\n"

        explained_var = results['explained_variance']
        summary += "\nExplained Variance Ratios:\n"
        for i, var in enumerate(explained_var):
            summary += f"PC{i + 1}: {var:.3f}\n"

        self.pcaresults_summary.insert(tk.END, summary)



    def update_figure(self):
        """Update the matplotlib figure."""
        self.canvas.draw()

    #### 6. UTILITY METHODS ####

    def save_plot(self):
        """Save the current plot to file."""
        try:
            if not os.path.exists(OUTPUT_DIR):
                os.makedirs(OUTPUT_DIR)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            plot_filename = f'plot_{timestamp}.png'
            save_path = os.path.join(OUTPUT_DIR, plot_filename)

            self.fig.savefig(save_path, bbox_inches='tight', dpi=300)
            messagebox.showinfo("Success", f"Plot saved as {save_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save plot: {str(e)}")


    def get_columns_to_drop(self):
        """Get list of columns to drop."""
        user_columns = [col.strip() for col in self.drop_entry.get().split(",") if col.strip()]
        return list(set(user_columns + DEFAULT_COLUMNS_TO_DROP))

    def get_cleaning_options(self):
        """Get data cleaning parameters."""
        return {
            'missing_strategy': self.missing_choice.get(),
            'bbch_filter': self.bbch_choice.get(),
            'drop_columns': self.get_columns_to_drop()
        }

    def get_target_variable(self):
        """Get selected target variable."""
        target_mode = self.target_mode.get()
        if target_mode == "BBCH":
            return "BBCH"
        elif target_mode == "Input Specific Target":
            return self.custom_target_entry.get().strip()
        return None

    def validate_data_exists(self):
        """Check if data is loaded."""
        if not hasattr(self, 'data') or self.data is None:
            messagebox.showerror("Error", "No file loaded. Please load a CSV file first.")
            return False
        return True

    def upload_mapping_csv(self):
        """Allow user to upload a mapping CSV file for feature-to-group mapping."""
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            messagebox.showerror("Error", "No file selected.")
            return

        try:
            # Load the CSV into a DataFrame
            df = pd.read_csv(file_path)

            # Validate the structure of the CSV
            if "Feature" not in df.columns or "Group" not in df.columns:
                messagebox.showerror("Error", "The mapping CSV must contain 'Feature' and 'Group' columns.")
                return

            # Load mapping using BiplotManager
            self.biplot_manager.load_group_mapping(df)

            # Store the mapping in the app
            self.feature_to_group = self.biplot_manager.feature_to_group
            self.feature_groups_colors = self.biplot_manager.group_colors

            # Enable analysis and visualization buttons
            self.enable_analysis_buttons()

            # Update results display with mapping information
            self.update_mapping_display(df)

            messagebox.showinfo("Success", "Feature-to-Group mapping loaded successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load mapping CSV: {str(e)}")

    def update_mapping_display(self, mapping_df):
        """Update the results display with mapping information."""
        try:
            # Enable text widget for editing
            self.featureresults_summary.config(state="normal")
            self.featureresults_summary.delete(1.0, tk.END)

            # Create summary text
            summary = "Feature-to-Group Mapping Summary:\n\n"
            for group in mapping_df['Group'].unique():
                features = mapping_df[mapping_df['Group'] == group]['Feature'].tolist()
                summary += f"{group}:\n"
                summary += "\n".join(f"- {feature}" for feature in features)
                summary += "\n\n"

            self.featureresults_summary.insert(tk.END, summary)
            self.featureresults_summary.config(state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating mapping display: {str(e)}")



    def enable_analysis_buttons(self):
        """Enable buttons for PCA analysis and visualizations."""
        self.visualize_button.config(state="normal")
        self.biplot_button.config(state="normal")
        self.interactive_biplot_button.config(state="normal")
        self.heatmap_button.config(state="normal")
        self.scree_plot_button.config(state="normal")
        self.top_features_button.config(state="normal")
        self.save_button.config(state="normal")

    def update_results_summary(self):
        """Update the PCA results summary text."""
        if hasattr(self, 'pca_model') and self.pca_model is not None:
            # Enable text widget for editing
            self.pcaresults_summary.config(state="normal")
            self.pcaresults_summary.delete(1.0, tk.END)

            # Add results
            explained_var = self.pca_model.explained_variance_ratio_
            cumulative_var = np.cumsum(explained_var)

            summary = "PCA Results Summary:\n\n"
            for i, (var, cum_var) in enumerate(zip(explained_var, cumulative_var)):
                summary += f"PC{i + 1}:\n"
                summary += f"- Explained variance: {var:.3f} ({var * 100:.1f}%)\n"
                summary += f"- Cumulative variance: {cum_var:.3f} ({cum_var * 100:.1f}%)\n\n"

            self.pcaresults_summary.insert(tk.END, summary)

            # Add loadings information if available
            if hasattr(self, 'x_standardized'):
                loadings = self.pca_model.components_.T
                feature_summary = "\nFeature Loadings Summary:\n\n"
                for i, feature in enumerate(self.x_standardized.columns):
                    feature_summary += f"{feature}:\n"
                    for j in range(loadings.shape[1]):
                        feature_summary += f"- PC{j + 1}: {loadings[i, j]:.3f}\n"
                    feature_summary += "\n"

                self.pcaresults_summary.insert(tk.END, feature_summary)

            self.pcaresults_summary.config(state="disabled")

    def update_target_input(self, *args):
        """Handle target input mode changes."""
        if self.target_mode.get() == "Input Specific Target":
            self.custom_target_entry.config(state="normal")
        else:
            self.custom_target_entry.delete(0, tk.END)
            self.custom_target_entry.config(state="disabled")

    def is_clean_data(self, data=None):
        """
        Check if the data meets the criteria for cleaned data.

        Parameters:
        -----------
        data : pandas.DataFrame, optional
            Data to check. If None, uses self.data

        Returns:
        --------
        bool
            True if data meets all cleaning criteria, False otherwise

        Notes:
        ------
        Criteria for clean data:
        1. No missing values
        2. All columns are numeric
        3. No infinity values
        """
        check_data = data if data is not None else self.data

        if check_data is None:
            return False

        try:
            # Check for missing values
            if check_data.isnull().values.any():
                return False

            # Check for numeric columns
            if not all(pd.api.types.is_numeric_dtype(check_data[col])
                       for col in check_data.columns):
                return False

            # Check for infinity values
            if np.isinf(check_data.values).any():
                return False

            return True

        except Exception as e:
            print(f"Error checking data cleanliness: {str(e)}")
            return False

    def clean_data(self, data, missing_strategy='impute_mean', bbch_filter=-1, drop_columns=None):
        """
        Clean and prepare data for PCA analysis.

        Parameters:
        -----------
        data : pandas.DataFrame
            Input data to be cleaned
        missing_strategy : str
            Strategy for handling missing values ('impute_mean', 'impute_median',
            'replace_nan', 'leave_empty')
        bbch_filter : int
            BBCH stage to filter by (-1 means no filter)
        drop_columns : list
            List of columns to drop from the dataset

        Returns:
        --------
        pandas.DataFrame
            Cleaned dataset

        Raises:
        -------
        ValueError
            If cleaning strategy is invalid or data cannot be cleaned
        """
        try:
            # Make a copy to avoid modifying the original data
            df = data.copy()

            # Store original shape for logging
            original_shape = df.shape

            # Drop specified columns
            if drop_columns:
                df = df.drop(columns=[col for col in drop_columns if col in df.columns])

            # Handle missing values based on strategy
            if missing_strategy == 'impute_mean':
                df = df.fillna(df.mean())
            elif missing_strategy == 'impute_median':
                df = df.fillna(df.median())
            elif missing_strategy == 'replace_nan':
                df = df.fillna(0)
            elif missing_strategy == 'leave_empty':
                df = df.dropna()
            else:
                raise ValueError(f"Invalid missing value strategy: {missing_strategy}")

            # Filter by BBCH stage if specified
            if bbch_filter != -1 and 'BBCH' in df.columns:
                df = df[df['BBCH'] == bbch_filter]

            # Convert non-numeric columns to numeric where possible
            for column in df.columns:
                if not pd.api.types.is_numeric_dtype(df[column]):
                    try:
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                    except:
                        print(f"Warning: Could not convert column {column} to numeric")

            # Replace infinity values with NaN and then handle them
            df = df.replace([np.inf, -np.inf], np.nan)
            if missing_strategy != 'leave_empty':
                df = df.fillna(df.mean())

            # Verify the cleaning was successful
            if not self.is_clean_data(df):
                raise ValueError("Data cleaning failed to produce valid data for PCA")

            # Store the cleaned data
            self.data = df
            self.cleaned_data = df

            print(f"Data cleaned successfully: {original_shape} -> {df.shape}")
            return df

        except Exception as e:
            raise ValueError(f"Error during data cleaning: {str(e)}")

    def analyze(self, data=None, n_components=2, drop_columns=None):
        """
        Perform PCA analysis on the data.

        Parameters:
        -----------
        data : pandas.DataFrame, optional
            Data to analyze (if None, uses cleaned_data)
        n_components : int
            Number of principal components to compute
        drop_columns : list, optional
            Additional columns to drop before analysis

        Returns:
        --------
        dict
            Dictionary containing PCA results

        Raises:
        -------
        ValueError
            If data is not clean or PCA cannot be performed
        """
        try:
            # Determine which data to use
            working_data = data if data is not None else self.cleaned_data
            if working_data is None:
                raise ValueError("No data available for analysis")

            # Verify data is clean before proceeding
            if not self.is_clean_data(working_data):
                raise ValueError("Data must be cleaned before analysis")

            # Drop additional columns if specified
            if drop_columns:
                working_data = working_data.drop(columns=[col for col in drop_columns
                                                          if col in working_data.columns])

            # Standardize the data
            self.standardized_data = self.scaler.fit_transform(working_data)

            # Perform PCA
            self.pca = PCA(n_components=n_components)
            transformed_data = self.pca.fit_transform(self.standardized_data)

            # Calculate cumulative explained variance
            cumulative_variance = np.cumsum(self.pca.explained_variance_ratio_)

            # Prepare comprehensive results
            results = {
                'model': self.pca,
                'standardized_data': pd.DataFrame(self.standardized_data,
                                                  columns=working_data.columns),
                'transformed_data': transformed_data,
                'explained_variance': self.pca.explained_variance_ratio_,
                'cumulative_variance': cumulative_variance,
                'n_components': n_components,
                'original_shape': working_data.shape,
                'prepared_shape': working_data.shape,
                'feature_names': working_data.columns.tolist()
            }

            return results

        except Exception as e:
            raise ValueError(f"Error during PCA analysis: {str(e)}")

    def get_feature_importance(self):
        """
        Get feature importance based on PCA loadings.

        Returns:
        --------
        pandas.DataFrame
            DataFrame containing feature importance scores and rankings
        """
        if self.pca is None:
            raise ValueError("PCA has not been performed yet")

        if self.cleaned_data is None:
            raise ValueError("No cleaned data available")

        # Calculate loadings
        loadings = pd.DataFrame(
            self.pca.components_.T,
            columns=[f'PC{i + 1}' for i in range(self.pca.n_components_)],
            index=self.cleaned_data.columns
        )

        # Calculate importance metrics
        loadings['mean_importance'] = loadings.abs().mean(axis=1)
        loadings['max_importance'] = loadings.abs().max(axis=1)
        loadings['contribution'] = (loadings ** 2).sum(axis=1)

        # Sort by mean importance
        loadings = loadings.sort_values('mean_importance', ascending=False)

        # Add rankings
        loadings['rank'] = range(1, len(loadings) + 1)

        return loadings









