import tkinter as tk
from tkinter import filedialog, messagebox
import traceback
import numpy as np
import pandas as pd

from sklearn.impute import SimpleImputer

from source.utils.constant import *


class CleanFileBox(tk.Frame):
    """
    Creates a space for file cleaning options
    """

    def __init__(self, main=None, df=None, **kwargs):
        super().__init__(main, **kwargs)


        # Variables
        self.missing_choice = None
        self.bbch_choice = None
        
        self.init_vars()

        # GUI Objects
        self.clean_data_banner = None
        self.clean_data_button = None

        self.missing_label = None
        self.impute_mean_radio = None
        self.impute_median_radio = None
        self.replace_nan_radio = None
        self.leave_empty_radio = None

        self.bbch_label = None
        self.bbch_none_radio = None
        self.bbch_59_radio = None
        self.bbch_69_radio = None
        self.bbch_85_radio = None

        self.drop_label = None
        self.drop_entry = None

        self.create_components()
        self.setup_layout()
        

    def init_vars(self):
        self.missing_choice = tk.StringVar(value="impute_mean")
        self.bbch_choice = tk.IntVar(value=-1)
        
    def create_components(self):
        self.clean_data_banner = tk.Label(self,
            text="Clean and/or Filter Data",
            font=("Helvetica", 12),
            bg="#dcdcdc",
            relief="groove")
        
        self.clean_data_button = tk.Button(self,
                                           text="Clean CSV",
                                           **BUTTON_STYLE,
                                           command=self.clean_data)

        # Missing Values Section
        self.missing_label = tk.Label(self,
                                      text="Handle Missing Values:",
                                      **LABEL_STYLE)
        self.impute_mean_radio = tk.Radiobutton(self,
                                                text="Impute with Mean",
                                                variable=self.missing_choice,
                                                value="impute_mean",
                                                **LABEL_STYLE)
        self.impute_median_radio = tk.Radiobutton(self,
                                                  text="Impute with Median",
                                                  variable=self.missing_choice,
                                                  value="impute_median",
                                                  **LABEL_STYLE)
        self.replace_nan_radio = tk.Radiobutton(self,
                                                text="Replace NaN with 0",
                                                variable=self.missing_choice,
                                                value="replace_nan",
                                                **LABEL_STYLE)
        self.leave_empty_radio = tk.Radiobutton(self,
                                                text="Leave Empty (Null)",
                                                variable=self.missing_choice,
                                                value="leave_empty",
                                                **LABEL_STYLE)

        # BBCH Selection
        self.bbch_label = tk.Label(self,
                                   text="Filter by BBCH Stage:",
                                   **LABEL_STYLE)
        self.bbch_none_radio = tk.Radiobutton(self,
                                              text="All (no filter)",
                                              variable=self.bbch_choice,
                                              value=-1,
                                              **LABEL_STYLE)
        self.bbch_59_radio = tk.Radiobutton(self,
                                            text="BBCH 59",
                                            variable=self.bbch_choice,
                                            value=59,
                                            **LABEL_STYLE)
        self.bbch_69_radio = tk.Radiobutton(self,
                                            text="BBCH 69",
                                            variable=self.bbch_choice,
                                            value=69,
                                            **LABEL_STYLE)
        self.bbch_85_radio = tk.Radiobutton(self,
                                            text="BBCH 85",
                                            variable=self.bbch_choice,
                                            value=85,
                                            **LABEL_STYLE)
        
        # Drop Columns Section
        self.drop_label = tk.Label(self,
                                   text="Columns to Drop (comma-separated):",
                                   **LABEL_STYLE)
        self.drop_entry = tk.Entry(self, width=30, **LABEL_STYLE)
 
    def setup_layout(self):
        # Configure component structure
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        
        # Clean Data Banner
        self.clean_data_banner.grid(row=0, column=0, columnspan=2,
                                    sticky="we", padx=5, pady=5)

        # Missing Values Section
        self.missing_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.impute_mean_radio.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.impute_median_radio.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.replace_nan_radio.grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.leave_empty_radio.grid(row=5, column=0, padx=5, pady=5, sticky="w")

        # BBCH Selection
        self.bbch_label.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.bbch_none_radio.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        self.bbch_59_radio.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        self.bbch_69_radio.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        self.bbch_85_radio.grid(row=5, column=1, padx=5, pady=5, sticky="w")

        # Clean Data Button
        self.clean_data_button.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        # Drop Columns Section
        self.drop_label.grid(row=9, column=0, padx=5, pady=5, sticky="e")
        self.drop_entry.grid(row=9, column=1, padx=5, pady=5, sticky="w")



    # Update internal variables
    def set_df(self, df):
        self.df = df
    


    #### 6. Data Handling ####

    def clean_data(self):
        """Clean the data and prepare it for PCA analysis."""

        '''
        if not self.df_loaded:
            messagebox.showinfo("Error", "Data must be loaded before it can be cleaned!")
            return  
        '''      

        try:
            # Convert int64 to float for PCA compatibility
            for col in self.df.columns:
                if self.df[col].dtype == 'int64':
                    self.df[col] = self.df[col].astype(float)

            # Ensure BBCH column exists and is treated as string
            if 'bbch' in self.df.columns:
                self.df['bbch'] = self.df['bbch'].astype(str).str.strip()

            # Filter by BBCH stage
            selected_bbch = self.bbch_choice.get()
            if selected_bbch == 59:
                self.df = self.df[self.df['bbch'] == 'B59']
            elif selected_bbch == 69:
                self.df = self.df[self.df['bbch'] == 'B69']
            elif selected_bbch == 85:
                self.df = self.df[self.df['bbch'] == 'B85']
            elif selected_bbch == -1:
                pass  # No filter applied if selected is -1 (all stages)

            # Drop user-specified columns
            self.df.columns = self.df.columns.str.strip().str.lower()  # Standardize column names
            self.drop_cols()

            # Drop non-numeric columns except BBCH
            if 'bbch' in self.df.columns:
                non_num_cols = self.df.select_dtypes(exclude=[float, int]).columns
                non_num_cols = non_num_cols.drop('bbch', errors='ignore')
                self.df.drop(columns=non_num_cols, inplace=True, errors='ignore')

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
            if self.df.isnull().any().any():
                x_imputed = imputer.fit_transform(self.df)
                self.df = pd.DataFrame(x_imputed, columns=self.df.columns)

            # Enable buttons and update UI
            self.visualize_button.config(state="normal")
            self.heatmap_button.config(state="normal")  # Enable heatmap button after cleaning
            self.update_data_info()
            messagebox.showinfo("Data Cleaned", "Data cleaned successfully and ready for PCA.")

            # Update Varibales tracking df status
            self.df_updated = True
            self.df_clean = True

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
        # Grabs the user entered columns to drop
        drop_cols =  [col.strip() for col in self.drop_entry.get().split(",") if col.strip()]
        drop_cols = [col.strip().lower() for col in drop_cols]  # Ensure consistency

        # Filter valid columns to drop
        valid_drop_cols = [col for col in drop_cols if col in self.df.columns]
        missing_cols = set(drop_cols) - set(self.df.columns)
        if missing_cols:
            print("Missing columns (not in dataset):", missing_cols)
        
        # Drop valid columns
        self.df.drop(columns=valid_drop_cols, inplace=True)

        return drop_cols


