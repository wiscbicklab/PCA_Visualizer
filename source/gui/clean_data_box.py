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


class CleanDataBox(tk.Frame):
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
        self.load_bttn = tk.Button(self, text="Browse", **BUTTON_STYLE, command=lambda: self.load_data(self.app_state))
        
        # Creates selector components for user input       
        self.missing_selector = MissingSelector(self, self.app_state, bg="#f0f0f0")
        self.filter_selector = FilterSelector(self, self.app_state, bg="#f0f0f0")
        
        # Creates widgets for selecting columns to drop
        self.drop_label = tk.Label(self, text="Columns to Drop (comma-separated):", **LABEL_STYLE)
        self.drop_entry = tk.Text(self, height=4, **BIG_ENTRY_STYLE)

        # Creates button for cleaning user data
        self.clean_bttn = tk.Button(self, text="Clean CSV", **BUTTON_STYLE, command=lambda: self.clean_data(self.app_state))
 
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

    def load_data(self, app_state: AppState):
        """
        Asks user to select a .csv data file and loads the data from the selected file
        
        Asks the user to select a .csv file. Loads the csv file into the app_state df
        Checks that the df was loaded correctly and udpates status variable respectfully
        If the data is loaded creates a new blank figure and updates the data info box text
        """
        # Loads Data
        df = file_ops.load_csv_file()
        if df is None:
            if self.app_state.df is not None:
                self.app_state.main.replace_status_text("Data File Not Selected: Previous Data Kept")
            else:
                self.app_state.main.replace_status_text("Data File Not Selected: Please Load Data")
            return
        app_state.df = df
        app_state.original_df = df.copy()

        # Updates df status variables
        app_state.df_updated.set(True)
        app_state.df_cleaned.set(False)

        main = app_state.main
        # Generate new blank figure
        main.create_blank_fig()    

        # Updates the GUI and shows sucess message
        main.replace_data_text(self.create_load_data_str(df))
        main.replace_status_text("Data Succsessfully Loaded!")


    def clean_data(self, app_state: AppState):
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
        if app_state.df is None:
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return  
        
        df = app_state.df

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
                messagebox.showerror("Select a Column", "No Column was selected for filtering")
                return  
            else:
                if filter_type == filters[1]:
                    if len(exact_value) == 0:
                        messagebox.showerror("No Values Selected", "Filtering by Values 'Equal to' was selected, but no value were entered")
                        return
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
        missing_user_drop_cols =  [col.strip().lower() for col in self.drop_entry.get('1.0', 'end-1c').split(",") if col.strip()]

        # Ensures the user columns exist and prints an error message with missing columns
        user_drop_cols = [col for col in missing_user_drop_cols if col in df.columns]
        missing_user_drop_cols = set(missing_user_drop_cols) - set(user_drop_cols)
        
        # Drops the columns from the dataset
        df.drop(columns=user_drop_cols, inplace=True)

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
        app_state.df = df
        app_state.df_updated.set(True)
        app_state.df_cleaned.set(True)


        main = app_state.main
        # Generate new blank figure
        main.create_blank_fig()

        # Updates the GUI and shows sucess message
        text = self.create_clean_data_str(df, user_drop_cols, missing_user_drop_cols, non_num_cols)
        main.replace_data_text(text)
        if len(missing_user_drop_cols) == 0:
            main.replace_status_text("Data Succsessfully Cleaned!")
        else:
            main.replace_status_text("Data Partially Cleaned! Check data section")
        

    #### 2. Generate Information Strings ####
    def create_load_data_str(self, df):
        text = "Data Information\n"
        text += "═══════════════════════════════════════\n\n"
        text += f"Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns\n\n"
        text += self.format_col_text(df.columns, "Columns:\t")

        return text
    
    def create_clean_data_str(self, df, user_drop_cols, missing_user_drop_cols, non_num_cols):
        text = "Cleaned Data Information\n"
        text += "═══════════════════════════════════════\n\n"

        text += self.format_col_text(user_drop_cols, "User Droped Columns:\t")
        text += self.format_col_text(missing_user_drop_cols, "User Drop Columns Not Found:\t")
        text += self.format_col_text(non_num_cols, "Non-numeric Columns Dropped:\t")
        text += "═══════════════════════════════════════\n\n"

        orig_rows = self.app_state.original_df.shape[0] #FIX THIS LOGIC
        orig_cols = self.app_state.original_df.shape[1]
        text += f"Original Dataset Shape: {orig_rows} rows × {orig_cols} columns\n"
        text += f"Cleanded Dataset Shape: {df.shape[0]} rows x {df.shape[1]} columns\n\n"
        text += self.format_col_text(df.columns, "Cleaned Columns:\t")
        
        return text    
    

    def format_col_text(self, cols, start_text="", line_limit=80, sep=",    "):
        if cols is None or len(cols) == 0:
            return start_text + "None\n"
        
        lines = []
        current_line = start_text
        for col in cols:
            item_str = (sep if current_line != start_text else "") + col
            if len(current_line) + len(item_str) > line_limit:
                lines.append(current_line)
                current_line = col
            else:
                current_line += item_str
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines) + "\n"
    