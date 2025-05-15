import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer

from source.gui.sub_components.bbch import BbchSelector
from source.gui.sub_components.missing import MissingSelector
from source.utils.constant import *


class CleanFileBox(tk.Frame):
    """
    GUI Frame for cleaning and filtering a loaded dataset using tkinter widgets.
    Allows users to handle missing values, filter by BBCH stage, and drop columns.
    """

    def __init__(self, main: tk.TK, **kwargs):
        super().__init__(main, **kwargs)
        self.main = main
        
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
        self.missing_selector = MissingSelector(self)
        self.bbch_selector = BbchSelector(self)
        
        # Column Dropping Selector
        self.drop_label = tk.Label(self,
                                   text="Columns to Drop (comma-separated):",
                                   **LABEL_STYLE)
        self.drop_entry = tk.Entry(self, width=30, **LABEL_STYLE)

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
        self.missing_selector.grid(row=1, column=0, sticky="we", padx=5, pady=5)
        self.bbch_selector.grid(row=1, column=1, sticky="we", padx=5, pady=5)

        # Column Dropping Selector
        self.drop_label.grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.drop_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Data Cleaning Button
        self.clean_bttn.grid(row=3, column=0, columnspan=2, padx=5, pady=5)


    #### 6. Data Handling ####

    def clean_data(self):
        """Clean the data and prepare it for PCA analysis."""

        '''
        if not self.main.df_loaded:
            messagebox.showinfo("Error", "Data must be loaded before it can be cleaned!")
            return  
        '''      

        try:
            # Convert int64 to float for PCA compatibility
            for col in self.main.df.columns:
                if self.main.df[col].dtype == 'int64':
                    self.main.df[col] = self.main.df[col].astype(float)

            # Ensure BBCH column exists and is treated as string
            if 'bbch' in self.main.df.columns:
                self.main.df['bbch'] = self.main.df['bbch'].astype(str).str.strip()

            # Filter by BBCH stage
            selected_bbch = self.bbch_choice.get()
            if selected_bbch != -1:
                self.main.df = self.main.df[self.main.df['bbch'] == f'B{selected_bbch}']

            # Drop user-specified columns
            self.main.df.columns = self.main.df.columns.str.strip().str.lower()  # Standardize column names
            self.drop_cols()

            # Drop non-numeric columns except BBCH
            if 'bbch' in self.main.df.columns:
                non_num_cols = self.main.df.select_dtypes(exclude=[float, int]).columns
                non_num_cols = non_num_cols.drop('bbch', errors='ignore')
                self.main.df.drop(columns=non_num_cols, inplace=True, errors='ignore')

            # Handle missing values
            if self.missing_choice.get() == "impute_mean":
                imputer = SimpleImputer(strategy='mean')
            elif self.missing_choice.get() == "impute_median":
                imputer = SimpleImputer(strategy='median')
            elif self.missing_choice.get() == "replace_nan":
                imputer = SimpleImputer(strategy='constant', fill_value=0)
            elif self.missing_choice.get() == "leave_empty":
                imputer = SimpleImputer(strategy='constant', fill_value=np.nan)
            else:
                messagebox.showerror("Error", "Please select a valid missing value handling strategy.")
                return

            # Impute missing values
            if self.main.df.isnull().any().any():
                x_imputed = imputer.fit_transform(self.main.df)
                self.main.df = pd.DataFrame(x_imputed, columns=self.main.df.columns)
            
            # Tells the container Widget do update the displayed data
            self.main.update_data_info()

            # Show Success Message after cleaning data
            messagebox.showinfo("Data Cleaned", "Data cleaned successfully and ready for PCA.")

            # Update Varibales tracking df status
            self.main.df_updated = True
            self.main.df_clean = True

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            messagebox.showerror("Error", f"An error occurred during data cleaning: {e}")

    def drop_cols(self) -> list:
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
        valid_drop_cols = [col for col in drop_cols if col in self.main.df.columns]
        missing_cols = set(drop_cols) - set(self.main.df.columns)
        if missing_cols:
            messagebox.showerror("Missing columns (not in dataset):", missing_cols)
        
        # Drops the columns from the dataset
        self.main.df.drop(columns=valid_drop_cols, inplace=True)

        return drop_cols


