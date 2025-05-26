import tkinter as tk
from tkinter import messagebox
import traceback
from matplotlib.figure import Figure
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer

from source.gui.clean_widgets.bbch import BbchSelector
from source.gui.clean_widgets.missing import MissingSelector
from source.gui.app_state  import AppState

from source.utils.constant import *


class CleanFileBox(tk.Frame):
    """
    GUI Frame for cleaning and filtering a loaded dataset using tkinter widgets.
    Allows users to handle missing values, filter by BBCH stage, and drop columns.
    """

    def __init__(self, main: tk.Tk,app_state: AppState, **kwargs):
        super().__init__(main, **kwargs)
        self.main = main
        self.app_state = app_state
        
        # Banner
        self.banner = None

        # Data Cleaning parameters
        self.missing_choice = tk.StringVar(value="impute_mean")
        self.bbch_choice = tk.IntVar(value=-1)

        # Data Cleaning Selectors
        self.missing_selector = None
        self.bbch_selector = None

        # Column Dropping Selector
        self.drop_label = None
        self.drop_entry = None

        # Data Cleaning Button
        self.clean_bttn = None

        # Intialize all Widgets in this frame and Setup Widget's in this Widget
        self.create_components()
        self.setup_layout()
        
    def create_components(self):
        """Create all tkinter widgets and components for the interface."""
        # Banner
        self.banner = tk.Label(self, text="Clean and/or Filter Data", 
                               font=("Helvetica", 12), bg="#dcdcdc", relief="groove")
        
        # Data Cleaning Selectors        
        self.missing_selector = MissingSelector(self, bg="#f0f0f0")
        self.bbch_selector = BbchSelector(self,bg="#f0f0f0")
        
        # Column Dropping Selector
        self.drop_label = tk.Label(self,
                                   text="Columns to Drop (comma-separated):",
                                   **LABEL_STYLE)
        self.drop_entry = tk.Entry(self, **LABEL_STYLE)

        # Data Cleaning Button
        self.clean_bttn = tk.Button(self, text="Clean CSV", **BUTTON_STYLE, 
                                    command=self.clean_data)
 
    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Banner
        self.banner.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        # Data Cleaning Selectors 
        self.missing_selector.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.bbch_selector.grid(row=1, column=1, padx=5, pady=5, sticky="nswe")

        # Column Dropping Selector
        self.drop_label.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")
        self.drop_entry.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nswe")

        # Data Cleaning Button
        self.clean_bttn.grid(row=4, column=0, columnspan=2, padx=5, pady=5)


    #### 6. Data Handling ####

    def clean_data(self):
        """Clean the data and prepare it for PCA analysis."""
        if not self.app_state.df_loaded:
            messagebox.showerror("Error", "Data must be loaded before it can be cleaned!")
            return  
        
        print(self.app_state.df_loaded)
            
        try:
            # Convert int64 to float for PCA compatibility
            for col in self.app_state.df.columns:
                if self.app_state.df[col].dtype == 'int64':
                    self.app_state.df[col] = self.app_state.df[col].astype(float)
            
            # Standardize column names
            self.app_state.df.columns = self.app_state.df.columns.str.strip().str.lower() 

            # Filter by BBCH stage
            selected_bbch = self.bbch_choice.get()
            if selected_bbch != -1:
                # Ensure BBCH column exists and is treated as string
                if 'bbch' in self.app_state.df.columns:
                    self.app_state.df['bbch'] = self.app_state.df['bbch'].astype(str).str.strip()
                    self.app_state.df = self.app_state.df[self.app_state.df['bbch'] == f"{float(selected_bbch):.1f}"]
                else:
                    messagebox.showerror("Error", "Could not clean data, bbch could not be found")
                    return
            
            # Drop user-specified columns
            self.drop_user_cols()

            # Drop non-numeric columns except BBCH
            if 'bbch' in self.app_state.df.columns:
                non_num_cols = self.app_state.df.select_dtypes(exclude=[float, int]).columns
                non_num_cols = non_num_cols.drop('bbch', errors="ignore")
                self.app_state.df.drop(columns=non_num_cols, inplace=True)

            # Drop Columns with no values
            self.app_state.df.dropna(axis=1, how='all', inplace=True)

            # Handle missing values
            if self.missing_choice.get() == "impute_mean":
                imputer = SimpleImputer(strategy='mean')
            elif self.missing_choice.get() == "impute_median":
                imputer = SimpleImputer(strategy='median')
            elif self.missing_choice.get() == "replace_nan":
                imputer = SimpleImputer(strategy='constant', fill_value=0)

            # Impute missing values
            if self.app_state.df.isnull().any().any():
                x_imputed = imputer.fit_transform(self.app_state.df)
                self.app_state.df = pd.DataFrame(x_imputed, columns=self.app_state.df.columns)
            
            # Update Varibales tracking df status
            self.app_state.df_updated = True
            self.app_state.df_cleaned = True

            # Generate new Blank figure
            self.app_state.fig = Figure()
            self.app_state.ax = self.app_state.fig.add_subplot(111)
            self.app_state.ax.grid(True)

            # Tells the container Widget do update the displayed data
            self.app_state.main.update_data_info()

                        # Show Success Message after cleaning data
            messagebox.showinfo("Data Cleaned", "Data cleaned successfully and ready for PCA.")


        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"An error occurred during data cleaning: {e}")

    def drop_user_cols(self) -> list:
        """
        Gets the user entered columns to drop and drops them from the df.
        Prints a messages about requested columns that couldn't nbe dropped

        Return:
            drop_cols: A list of the columns that were dropped from the data
            missing_cols: A list of the columns that were requested to be 
                        dropped but could not be dropped
        """
        # Grabs the user entered columns to drop and cleans the input
        drop_cols =  [col.strip() for col in self.drop_entry.get().split(",") if col.strip()]
        drop_cols = [col.strip().lower() for col in drop_cols]

        # Ensures the user columns exist and prints an error message with missing columns
        valid_drop_cols = [col for col in drop_cols if col in self.app_state.df.columns]
        missing_cols = set(drop_cols) - set(self.app_state.df.columns)
        if missing_cols:
            messagebox.showerror("Missing columns (not in dataset):", missing_cols)
        
        # Drops the columns from the dataset
        self.app_state.df.drop(columns=valid_drop_cols, inplace=True)

        return drop_cols


