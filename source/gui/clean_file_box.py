import tkinter as tk
from tkinter import messagebox
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer

from source.gui.clean_widgets.bbch import BbchSelector
from source.gui.clean_widgets.missing import MissingSelector
from source.gui.app_state  import AppState

from source.utils.constant import *


class CleanFileBox(tk.Frame):
    """
    Creates a space for the user to clean their data

    Args:
        main: tk.Widget
            The parent widget for this frame.
        app_state: AppState
            The app_state variable used to pass data between components
        **kwargs: dict
            Additional keyword arguments passed to tk.Frame.
    """

    #### 0. Setup GUI Elements ####

    def __init__(self, main: tk.Tk, app_state: AppState, **kwargs):
        """Initializes box for cleaning user data"""
        # Intializes data about the container class
        super().__init__(main, **kwargs)
        self.app_state = app_state
        
        # Declares frame banner
        self.banner = None

        # Declare selector components for user input
        self.missing_selector = None
        self.bbch_selector = None

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
        self.banner = tk.Label(self, text="Clean and/or Filter Data", **BANNER_STYLE)
        
        # Creates selector components for user input       
        self.missing_selector = MissingSelector(self, bg="#f0f0f0")
        self.bbch_selector = BbchSelector(self,bg="#f0f0f0")
        
        # Creates widgets for selecting columns to drop
        self.drop_label = tk.Label(self, text="Columns to Drop (comma-separated):", **LABEL_STYLE)
        self.drop_entry = tk.Entry(self, **ENTRY_STYLE)

        # Creates button for cleaning user data
        self.clean_bttn = tk.Button(self, text="Clean CSV", **BUTTON_STYLE, command=self.clean_data)
 
    def setup_layout(self):
        """Sets the components onto this tk Frame"""
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Places banner at the top of this component
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Places selector components next to each other
        self.missing_selector.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.bbch_selector.grid(row=1, column=1, padx=5, pady=5, sticky="nswe")

        # Places column dropping widgets
        self.drop_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")
        self.drop_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")

        # Places data cleaning button
        self.clean_bttn.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


    #### 1. Data Handling ####

    def clean_data(self):
        """Cleans the data based on the user selections in preperation for PCA Analysis"""
        # Validates that the data has been loaded
        if not self.app_state.df_loaded.get():
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return  
        
        df = self.app_state.df

        # Convert int64 to float for PCA compatibility
        int_cols = df.select_dtypes(include='int64').columns
        df[int_cols] = df[int_cols].astype(float)

        # Standardize column names
        df.columns = df.columns.str.strip().str.lower() 

        # Filter by BBCH stage
        selected_bbch = self.app_state.bbch_choice.get()
        if selected_bbch != -1:
            # Ensure BBCH column exists and is treated as string
            if 'bbch' in df.columns:
                df = df[np.isclose(df['bbch'], float(selected_bbch), atol=0.05)]
            else:
                messagebox.showerror(
                    "Error", 
                    "Could not clean data. BBCH filtering selected but, BBCH could not be found"
                )
                return
        
        # Drop user-specified columns
        self.drop_user_cols(df)

        # Drop non-numeric columns and columns with no values
        non_num_cols = df.select_dtypes(exclude=[float, int]).columns
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

    def drop_user_cols(self, df) -> list:
        """
        Gets the user entered columns to drop and drops them from the df.
        Prints a messages about requested columns that couldn't nbe dropped

        Args:
            df: The dataframe to drop columns from
        """
        # Grabs the user entered columns to drop and cleans the input
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


