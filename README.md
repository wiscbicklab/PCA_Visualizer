# PCA Tool

## GUI File Structure

```
PCA_11.27.24-pca/
│
├── requirements.txt           ← Python dependencies
│
└── source/
    ├── analysis/
    │   └── pca.py             ← Core PCA computation
    │
    ├── gui/
    │   ├── app.py             ← Main GUI application (tkinter)   
    │   └── spillover.py       ← Event bindings & interactivity helpers
    │
    ├── utils/
    │   ├── constant.py        ← Column/feature definitions, defaults
    │   ├── file_operations.py ← CSV loading/saving utilities
    │   └── helpers.py         ← Data cleaning, transformation utilities
    │
    └── visualization/
        ├── base.py            ← Plotting foundation
        ├── biplot.py          ← PCA biplot rendering
        └── heatmap.py         ← Heatmap rendering
```

## Development Notes

### For updating:

- `app.py` is the GUI control hub  
    To run and debug from IDE, add the following to the bottom of app.py:
    
    ```python
    if __name__ == "__main__":  
        root = tk.Tk()  
        app = PCAAnalysisApp(root)  
        root.mainloop()
    ```
    
- `pca.py` contains logic for dimension reduction and variance calculation
    
- Consider extending plotting capabilities in `biplot.py` and `heatmap.py`
    
- Constants (e.g., feature groups, default columns to drop) are stored in `constant.py`
    

### Technical Notes

- Interactive plots use `plotly` (check dependencies)
- Color grouping maps must be CSVs with valid column-to-group mappings
- Filtering BBCH values is case-sensitive: ensure data uses formats like `"B69"`

## GUI Features Overview

### Data Loading & Preparation

- **Load a CSV file**: Use the file browser to choose a dataset
    
- **Clean and Filter Data**:
    
    - Handle missing values (mean, median, 0, or null)
    - Filter by specific BBCH growth stages (B59, B69, B85)
        - _Note: BBCH stages are relevant to the KU team/data Emily was working with_
    - Drop unwanted columns

### Analysis

- **Run PCA (Principal Component Analysis)**:
    - Select how many components to extract
    - Choose how many top features to display in the biplot
    - Label axes based on a target variable (if desired)
        - PCA reduces dimensionality based only on numerical features — the **target variable is not included** in this reduction
        - When visualizing results, the **target variable is used to color data points** to show class distribution in PCA space

### Visualization

- **View Results**:
    - Scree plots
    - Standard or grouped biplots (colored by label or cluster)
    - Heatmaps of top PCA-contributing features
- **Save Outputs**:
    - Cleaned CSV
    - Scree plot, biplot, heatmap (static and/or interactive)

## Testing Workflow

1. Download the executable from: [https://github.com/wiscbicklab/PCA_11.27.24/releases/tag/pca](https://github.com/wiscbicklab/PCA_11.27.24/releases/tag/pca)
    
2. Download `KUPCA_GUI.exe`
    
3. Open from browser's downloads
    
    - You may need to override security warnings by selecting 'run anyway' or right-clicking to 'run as administrator'
4. Maximize the window for optimal viewing
    

### Using the Tool

1. **Upload Data**:
    
    - Click Browse and select `USE_THIS_updated_encoded_cleaned_SC_all_BBCH_final.csv`
2. **Configure Preprocessing**:
    
    - Copy/paste the list of columns to drop from the 'columns to drop' file
    - Optionally filter to a specific BBCH stage
3. **Clean the Data**:
    
    - Click "Clean CSV"
4. **Configure PCA Settings**:
    
    - Default shows 10 most significant features (adjustable)
5. **Run Analysis**:
    
    - Click "Run PCA" then "Visualize PCA"
    - For feature grouping, load the `KUPCA_featuregroups.csv` file
6. **Explore Results**:
    
    - Use "Biplot with Groups" for exploratory analysis
    - Check "Top Loadings" to see feature rankings
    - For more than 2 principal components, adjust the component number textbox from the default 2, then run PCA again

## Known Issues That Need Fixing:

1. Visualization: Group colors are not being applied correctly (grayed out option)
2. Feature Mapping: Enable/disable logic not functioning properly
3. Heatmap: Currently showing index of features instead of top features

## Future Enhancements

- Fix the highlighted issues
- Generalize BBCH-specific filtering to support custom categorical filters
- Improve interactive plotting capabilities
- Enhance feature grouping functionality
- Add more customization (e.g. user decides color palette) 
