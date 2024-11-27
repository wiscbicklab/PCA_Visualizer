import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, Optional, List, Tuple
import traceback


class PCAAnalyzer:
    """Core PCA analysis functionality separate from GUI."""

    def __init__(self):
        self.pca_model = None
        self.standardized_data = None
        self.feature_groups = None
        self.x_standardized = None

    def prepare_data(
            self,
            data: pd.DataFrame,
            drop_columns: Optional[List[str]] = None,
            default_columns_to_drop: Optional[List[str]] = None
    ) -> Tuple[pd.DataFrame, List[str]]:
        """Prepare data for PCA analysis."""
        # Create working copy
        working_data = data.copy()

        # Validate user-specified columns exist
        if drop_columns:
            missing_columns = [col for col in drop_columns if col not in working_data.columns]
            if missing_columns:
                raise ValueError(f"Columns not found in the dataset: {', '.join(missing_columns)}")
            working_data = working_data.drop(columns=drop_columns)

        # Drop predefined columns
        if default_columns_to_drop:
            default_to_drop = [col for col in default_columns_to_drop if col in working_data.columns]
            working_data = working_data.drop(columns=default_to_drop)

        return working_data, missing_columns if drop_columns else []

    def validate_numeric_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Extract and validate numeric data with detailed checks."""
        # Select numeric data
        numeric_data = data.select_dtypes(include=[np.number])

        # Identify and log non-numeric columns
        removed_columns = data.columns.difference(numeric_data.columns)
        if not removed_columns.empty:
            print(f"Non-numeric columns excluded: {list(removed_columns)}")

        # Check if numeric data is empty
        if numeric_data.empty:
            raise ValueError("No numerical data available for PCA")

        # Replace inf values with NaN
        if np.any(np.isinf(numeric_data.values)):
            numeric_data = numeric_data.replace([np.inf, -np.inf], np.nan)

        return numeric_data

    def standardize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Standardize the data for PCA with detailed tracking."""
        print(f"Data shape before standardization: {data.shape}")  # Debug info




        scaler = StandardScaler()
        standardized = pd.DataFrame(
            scaler.fit_transform(data),
            columns=data.columns
        )
        self.standardized_data = standardized
        self.x_standardized = standardized  # Keep original attribute



        print(f"Data shape after standardization: {standardized.shape}")  # Debug info
        return standardized

    def run_pca(self, data: pd.DataFrame, n_components: int) -> Dict[str, Any]:
        """Run PCA analysis with detailed validation and debugging."""
        # Validate components and data
        print(f"\nDEBUG INFO BEFORE PCA:")
        print(f"Data shape before PCA: {data.shape}")
        print(f"Number of components requested: {n_components}")

        max_components = data.shape[1]
        print(f"Maximum components allowed: {max_components}")

        if n_components > max_components:
            n_components = max_components
            print(f"Capping components to {max_components}.")

        # PCA Execution with detailed tracking
        print("\nStarting PCA fit...")
        self.pca_model = PCA(n_components=n_components)
        print("PCA model initialized")

        transformed_data = self.pca_model.fit_transform(data)
        print("PCA fit completed")

        # Debug output
        print("\nPCA Results:")
        print(f"PCA components shape: {self.pca_model.components_.shape}")
        print(f"Explained variance ratios: {self.pca_model.explained_variance_ratio_}")

        # Return comprehensive results
        return {
            'model': self.pca_model,
            'transformed_data': transformed_data,
            'components': self.pca_model.components_,
            'explained_variance': self.pca_model.explained_variance_ratio_,
            'loadings': self.pca_model.components_.T,
            'feature_names': data.columns.tolist(),
            'n_components': n_components,
            'max_components': max_components,
            'data_shape': data.shape
        }

    def analyze(
            self,
            data: pd.DataFrame,
            n_components: int,
            drop_columns: Optional[List[str]] = None,
            default_columns_to_drop: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Complete PCA analysis pipeline with comprehensive error handling."""
        try:
            # Prepare and validate data
            prepared_data, missing_columns = self.prepare_data(
                data,
                drop_columns=drop_columns,
                default_columns_to_drop=default_columns_to_drop
            )

            # Process numeric data
            numeric_data = self.validate_numeric_data(prepared_data)

            # Standardize
            standardized_data = self.standardize_data(numeric_data)

            # Run PCA
            results = self.run_pca(standardized_data, n_components)

            # Add additional context to results
            results.update({
                'missing_columns': missing_columns,
                'original_shape': data.shape,
                'prepared_shape': prepared_data.shape,
                'standardized_shape': standardized_data.shape
            })

            return results

        except Exception as e:
            traceback.print_exc()  # Keep detailed error tracking
            raise Exception(f"PCA analysis failed: {str(e)}")