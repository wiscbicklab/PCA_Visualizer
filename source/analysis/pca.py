import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Optional, List, Tuple
import traceback

class PCAAnalyzer:
    """
    Core PCA analysis functionality
    """

    def prepare_data(
            self,
            df: pd.DataFrame,
            drop_cols: Optional[List[str]] = None,
            default_drop_cols: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, List[str]]:
        """
        Removes the specified columns from the data

        Args:
            df (pd.DataFrame): Data to prepare
            drop_cols (List[str]): The names of the columns to remove from the data
            default_drop_cols (List[str]): The names of 'default' columns to remove from the data

        Return:  
            DataFrame: A copy of data with the specified columns filtered out
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Input must be a pandas DataFrame, but got {type(df).__name__}")

        # Create working copy
        df_copy = df.copy()

        # Validate user-specified columns exist
        if drop_cols:
            missing_cols = [col for col in drop_cols if col not in df_copy.columns]
            if missing_cols:
                raise ValueError(f"Columns not found in the dataset: {', '.join(missing_cols)}")
            df_copy = df_copy.drop(columns=drop_cols)

        # Drop predefined columns
        if default_drop_cols:
            default_to_drop = [col for col in default_drop_cols if col in df_copy.columns]
            df_copy = df_copy.drop(columns=default_to_drop)

        return df_copy, missing_cols if drop_cols else []

    def clean_numeric_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Excludes and prints non-numeric columns. Cleans numeric data by replacing inf values with NaN
        
        Args:
            df (pd.DataFrame): Data to validate
        
        Return:
            (pd.DataFrame): The numeric data from the given data with cleaned values.
        """
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Input must be a pandas DataFrame, but got {type(df).__name__}")

        # Select numeric data
        numeric_df = df.select_dtypes(include=[np.number])

        # Check if numeric data is empty
        if numeric_df.empty:
            raise ValueError("No numerical data available for PCA")

        # Identify and log non-numeric columns
        rm_cols = df.columns.difference(numeric_df.columns)
        if not rm_cols.empty:
            print(f"Non-numeric columns excluded: {list(rm_cols)}")

        # Replace inf values with NaN
        if np.any(np.isinf(numeric_df.values)):
            numeric_df = numeric_df.replace([np.inf, -np.inf], np.nan)

        return numeric_df, rm_cols
  
    def standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize the data for PCA with detailed tracking.
        
        Args:
            df (pd.DataFrame): Data to be standardized
        Return:
            (pd.DataFrame): Standardized data
        """
        # Validate Input data
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Input must be a pandas DataFrame, but got {type(df).__name__}")

        # Standardize Data
        standardized = pd.DataFrame(StandardScaler().fit_transform(df), columns=df.columns)

        return standardized

    def run_pca(self, df: pd.DataFrame, n_components: int) -> Dict[str, Any]:
        """
        Run PCA analysis with detailed validation and debugging.
        
        Args:
            df (pd.DataFrame): Numeric data to run PCA on.
            dimensions (int):  Number of components for PCA to divide the data into
            n_components (int): Number of components to run PCA on

        Return:
            A dictionary of useful information regaurding the PCA model
                'model': model,
                'transformed_data': transformed_data,
                'components': model.components_,
                'explained_variance': model.explained_variance_ratio_,
                'loadings': model.components_.T,
                'feature_names': df.columns.tolist(),
                'n_components': n_components,
                'max_components': max_components,
                'data_shape': df.shape
        """
        # Gets the number of data entries in the df
        max_components = df.shape[1]

        # Verifies parameter types
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Input must be a pandas DataFrame, but got {type(df).__name__}")
        if n_components > df.shape[1]:
            raise ValueError("More components selected then exist")

        # PCA Execution with detailed tracking
        model = PCA(n_components=n_components)
        transformed_data = model.fit_transform(df)

        # Return comprehensive results
        return {
            'model': model,
            'transformed_data': transformed_data,
            'components': model.components_,
            'explained_variance': model.explained_variance_ratio_,
            'loadings': model.components_.T,
            'feature_names': df.columns.tolist(),
            'n_components': n_components,
            'max_components': max_components,
            'data_shape': df.shape
        }

    def analyze(
            self,
            df: pd.DataFrame,
            n_components: int,
            drop_cols: Optional[List[str]] = None,
            default_drop_cols: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Complete PCA analysis pipeline with comprehensive error handling.
        
        Args:
            df (pd.DataFrame): Data to run the PCA analysis on
            n_components (int): Number of components to run PCA on
            drop_cols (List[str]): The names of the columns to remove from the data
            default_drop_cols (List[str]): The names of 'default' columns to remove from the data

        Return:
            A dictionary of useful information regaurding the PCA model
                'model': model,
                'transformed_data': transformed_data,
                'components': model.components_,
                'explained_variance': model.explained_variance_ratio_,
                'loadings': model.components_.T,
                'feature_names': df.columns.tolist(),
                'n_components': n_components,
                'max_components': max_components,
                'data_shape': df.shape
                'missing_columns': missing_columns,
                'original_shape': df.shape,
                'prepared_shape': prepared_data.shape,
                'standardized_shape': standardized_data.shape
        """
        try:
            # Prepare and validate data
            prepared_data, missing_cols = self.prepare_data(
                df,
                drop_cols=drop_cols,
                default_drop_cols=default_drop_cols
            )

            # Clean numeric data
            numeric_data, missing_cols = self.clean_numeric_data(prepared_data)

            # Standardize
            standardized_data = self.standardize_data(numeric_data)

            # Run PCA
            results = self.run_pca(standardized_data, n_components)
            # Add additional context to results
            results.update({
                'missing_columns': missing_cols,
                'original_shape': df.shape,
                'prepared_shape': prepared_data.shape,
                'standardized_shape': standardized_data.shape,
                'standardized_data': standardized_data,
            })

            return results

        except Exception as e:
            error_str = traceback.print_exc()  # Keep detailed error tracking
            print(error_str)
            raise Exception(f"PCA analysis failed: {str(e)}")