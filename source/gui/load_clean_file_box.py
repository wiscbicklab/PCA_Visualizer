import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer

from source.gui.clean_widgets.filter_selector import FilterSelector
from source.gui.clean_widgets.missing_selector import MissingSelector
from source.gui.app_state  import AppState
import source.utils.file_operations as file_ops

from source.utils.constant import *


class CleanFileBox(tk.Frame):
    """
    A GUI box for loading data, selecting cleaning options, and cleaning data

    A banner indicating the usage of this container
    A text prompt and button allowing for users to load a .csv file
    Two columns, The left column containg another GUI box for selecting how to Handle Missing inputs
                 The right column gontaining another GUI box for selecting what BBCH stage filter to use
    An optional entry box for droping columns from the loaded data
    A button for cleaning the CSV
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs):
        """
        Creates a space for loading and cleaning user data

        Args:
            main: tk.Widget
                The parent widget for this frame.
            app_state: AppState
                The app_state variable used to pass data between components
            **kwargs: dict
                     # Intializes data about the container class
        """
        super().__init__(main, **kwargs)
        self.app_state = app_state
        
        # Declare frame banner
        self.banner = None

        # Declare loading components
        self.load_label = None
        self.load_bttn = None

        # Declare selector components for user input
        self.missing_selector = None
        self.filter_selector = None

        # Declare widgets for selecting columns to drop
        self.drop_label = None
        self.drop_entry = None

        # Declare button for cleaning user data
        self.clean_bttn = None

        # Creates components and sets them within the GUI
        self.create_components()
        self.setup_layout()
        
    def create_components(self):
        """Creates the components to be placed onto this tk Frame"""
        # Creates frame banner
        self.banner = tk.Label(self, text="Load, Clean, and Filter Data", **BANNER_STYLE)

        # Creates loading components
        self.load_label =  tk.Label(self, text="Load CSV File:", **LABEL_STYLE)
        self.load_bttn = tk.Button(self, text="Browse", **BUTTON_STYLE, command=self.load_data)
        
        # Creates selector components for user input       
        self.missing_selector = MissingSelector(self, self.app_state, bg="#f0f0f0")
        self.filter_selector = FilterSelector(self, self.app_state, bg="#f0f0f0")
        
        # Creates widgets for selecting columns to drop
        self.drop_label = tk.Label(self, text="Columns to Drop (comma-separated):", **LABEL_STYLE)
        self.drop_entry = tk.Entry(self, **BIG_ENTRY_STYLE)

        # Creates button for cleaning user data
        self.clean_bttn = tk.Button(self, text="Clean CSV", **BUTTON_STYLE, command=self.clean_data)
 
    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Places banner at the top of this component
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Places loading components below the banner
        self.load_label.grid(row=1, column=0, padx=5, pady=5)
        self.load_bttn.grid(row=1, column=1, padx=5, pady=5)

        # Places selector components next to each other
        self.missing_selector.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.filter_selector.grid(row=2, column=1, padx=5, pady=5, sticky="nswe")

        # Places column dropping widgets
        self.drop_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")
        self.drop_entry.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")

        # Places data cleaning button
        self.clean_bttn.grid(row=5, column=0, columnspan=2, padx=5, pady=5)


    #### 1. Data Handling ####

    def load_data(self):
        """
        Asks user to select a .csv data file and loads the data from the selected file
        
        Asks the user to select a .csv file. Loads the csv file into the app_state df
        Checks that the df was loaded correctly and udpates status variable respectfully
        If the data is loaded creates a new blank figure and updates the data info box text
        """
        self.app_state.df = file_ops.load_csv_file()

        # Check that the data has been loaded correctly
        if self.app_state.df is None:
            self.app_state.df_cleaned.set(False)
            return

        # Updates df status variables
        self.app_state.df_updated.set(True)
        self.app_state.df_cleaned.set(False)

        # Generate new blank figure
        self.app_state.main.create_blank_fig()    

        # Updates the GUI and shows sucess message
        self.app_state.main.update_data_info()
        messagebox.showinfo("Success", "File loaded successfully")

    def clean_data(self):
        """
        Cleans the data based on the user selections in preperation for PCA Analysis
        
        Converts all int64 columns to float columns
        Standardizes the column names by stripping whitespace and setting text to lower case
        Filters the data by the selected bbch
        Verifies and drops the user selected columns. Shows an error if columns are missing
        Drops Non-numeric columns and columns with no data
        Uses the user selected filtering/imputing method to fill in blank data values
        Creates a new blank figure and updates the data info box text 
        """
        # Validates that the data has been loaded
        if self.app_state.df is None:
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return  
        
        df = self.app_state.df

        # Convert int64 to float for PCA compatibility
        int_cols = df.select_dtypes(include='int64').columns
        df[int_cols] = df[int_cols].astype(float)

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower() 

        # Get filter values
        filter_name = self.app_state.custom_filter_target.get().lower().strip()
        filter_type = self.app_state.custom_filter_type.get()
        exact_value = [col.strip().lower() for col in self.app_state.custom_filter_equal.get().split(",") if col.strip()]
        lower_value = float(self.app_state.custom_filter_lower.get())
        upper_value = float(self.app_state.custom_filter_upper.get())

        # Filter based on the filter selection
        filters = ["None", "Equal to", "Less than", "Greater than", "Between", "Outside"]
        if filter_type != filters[0]:
            if filter_name not in df.columns:
                messagebox.showerror("Column Label Error", f"The selected column, {filter_name}, was not found in the data.\nSkipping filtering!")
            elif filter_name == "":
                messagebox.showinfo("Select a Column", "No Column was selected for filtering")
                
            else:
                if filter_type == filters[1]:
                    if len(exact_value) == 0:
                        messagebox.showinfo("No Values Selected", "Filtering by Values 'Equal to' was selected, but no value were entered")
                    exact_value_floats = [float(val) for val in exact_value]
                    df = df[df[filter_name].apply(lambda x: any(np.isclose(x, v, atol=0.001) for v in exact_value_floats))]
                elif filter_type == filters[2]:
                    df = df[df[filter_name] < upper_value]
                elif filter_type == filters[3]:
                    df = df[df[filter_name] > lower_value]
                elif filter_type == filters[4]:
                    df = df[(df[filter_name] > lower_value) & (df[filter_name] < upper_value)]
                elif filter_type == filters[5]:
                    df = df[(df[filter_name] < lower_value) | (df[filter_name] > upper_value)]
                else:
                    messagebox.showerror("Application Error", "An internal program error has occurred getting filter type")
        
        # Drop user-specified columns
        drop_cols =  [col.strip().lower() for col in self.drop_entry.get().split(",") if col.strip()]

        # Ensures the user columns exist and prints an error message with missing columns
        valid_drop_cols = [col for col in drop_cols if col in df.columns]
        missing_cols = set(drop_cols) - set(df.columns)
        if missing_cols:
            messagebox.showerror(
                "Error Dropping Columns", 
                f"Missing columns (not in dataset):\t{missing_cols}\nMissing columns will be ignored."
            )
        
        # Drops the columns from the dataset
        df.drop(columns=valid_drop_cols, inplace=True)

        # Drop non-numeric columns and columns with no values
        non_num_cols = df.select_dtypes(exclude=[float]).columns
        df.drop(columns=non_num_cols, inplace=True)
        df.dropna(axis=1, how='all', inplace=True)

        # Determine how to filter/interpolate data
        missing_choice = self.app_state.missing_choice.get()
        if missing_choice == "impute_mean":
            imputer = SimpleImputer(strategy='mean')
        elif missing_choice == "impute_median":
            imputer = SimpleImputer(strategy='median')
        elif missing_choice == "replace_nan":
                imputer = SimpleImputer(strategy='constant', fill_value=0)

            # Impute missing values
        
        # Filter/Interpolate data
        if df.isnull().any().any():
            x_imputed = imputer.fit_transform(df)
            df = pd.DataFrame(x_imputed, columns=df.columns)
        
        # Update varibales tracking df status
        self.app_state.df = df
        self.app_state.df_updated.set(True)
        self.app_state.df_cleaned.set(True)

        # Generate new blank figure
        self.app_state.main.create_blank_fig()

        # Updates the GUI and shows sucess message
        self.app_state.main.update_data_info()
        messagebox.showinfo("Data Cleaned", "Data cleaned successfully and ready for PCA.")
        


