# PCA Tool

## GUI File Structure

```
PCA_11.27.24-pca/
│
├── requirements.txt                ← Python dependencies
│
└── source/
    ├── analysis/
    │   └── pca.py                  ← Core PCA computation
    │
    ├── gui/
    │   ├─ clean_widgets/
    |   |   ├── bbch_selector.py    ← GUI checkbox for filtering by bbch (Depreciated)
    │   │   ├── filter_selector.py  ← GUI selector for filtering by a selected column
    |   |   └── missing_selector.py ← GUI checkbox for filtering/interpolating missing data
    |   |
    │   ├── app.py                  ← Main GUI application (tkinter)  
    |   ├── app_state.py            ← AppState object is used to pass information between GUI widgets
    │   ├── clean_data_box.py       ← GUI functionality for loading and cleaning data 
    │   ├── create_plot_box.py      ← GUI functionality for creating several types of plots
    │   └── settings_box.py         ← GUI functionality for changing parameters for plot generation
    │
    └── utils/
        ├── constant.py             ← Styling and Theme 
        ├── file_operations.py      ← CSV loading/saving utilities
        └── input_validation.py     ← Validation commands for user input
```

## How to start the application

- To run on Linux
  - Clone the repository, ```git clone https://github.com/wiscbicklab/PCA_11.27.24.git```
  - Open the repository, ```cd PCA_11.27.24```
  - Create a virtual enviroment, ```python -m venv NAME_OF_ENVIROMENT```
  - Activate the enviroment, ```source NAMEOF_ENVIROMENT/bin/activate```
  - Install dependencies, ```pip install adjustText chardet matplotlib numpy pandas plotly scikit-learn seaborn screeninfo```
  - Run application as a module, ```python -m source.gui.app```
    
- To run on Windows
  - Download the .exe from the latest release at https://github.com/wiscbicklab/PCA_11.27.24/releases
  - Run the .exe
    - You may need to override security warnings by right-clicking to 'run as administrator'
    - The .exe may take a while to launch especially during first launch

## How to use the application

1. **Upload Data**:
    - At the top of the application click the 'Browse' button next to 'Load CSV File:' text
    - Select a csv file from the pop up.
      - The first row of the csv file should be the names of the data in each column
      - Each additional row represents a collection of data, ie a data point

2. **Clean the Data**:
    - Select options for how to clean the data
      - Select an option for how to deal with missing values in the data
      - Select an option for how filtering by column
        - Select A filter type
          - None.         No filter is applied. All rows are included
          - Equal to.     Selects all rows where the value of selected column is within .001 of the given Values
          - Less than:    Selects all rows where the value of selected column is less than the Upper Bound(Exclusive)
          - Greater than: Selects all rows where the value of selected column is greater than the Lower Bound(Exclusive)
          - Between:      Selects all rows where the value of selected column is betwee the Lower and Upper Bound(Exclusive)
          - Outside:      Selects all rows where the value of selected column is less than the Lower Bound(Exclusive) or greater than the Upper Bound(Exclusive)
        - Select the Datat column to filter by
        - Enter the bounds for the selected filter
          - If entering Values seperate the values by commas.
      - Enter any columns you would like to remove from the PCA analysis seperated by columns
        IE. (year, rep, SAMPLENUM)
    - Click on the 'Clean CSV' button

3. **Generate Plots**:
    - Click the 'Plot PCA' button to create a visualization of all points in the first two Principle Components
    - Click the 'Plot Heatmap' button to create a heatmap of the top features
    - Click the 'Biplot' button to generate a Biplot over the first two Principle Components
    - Click the 'Interactive Biplot' button to generate an interactive biplot. This will be saved as an html file and opened in your browser
    - Click the 'Scree Plot' button to generate a scree plot with the PCA results
    - Click the 'Feature Loadings Plot' button to generate a bar plot of the absolute loadings. Sorted by top values on the selected PCA component

4. **Configure Settings**:
    - Change the Number of 'PCA Components'
      - Determines the number of PCA components shown on the Scree Plot and heatmap
    - Change the 'Number of Features'
      - Determines the number of features to show on the Biplot, Interactive Biplot, Feature Loadings Plot, and Heatmap
    - Change the "Focused PCA Component"
      - Determines which PCA component to sort feature loadings by for the Heatmap
      - Determines Which PCA component to show the top features for on the Feature Loadings Plot
    - Add a 'PCA Plot Target'
      - This adds groups to the PCA Plot for the selected target feature
      - For up to 20 values of the selected feature a unique color is assigned
      - If more than 20 value exist the values are grouped together with each group having the same number of unique values
    - Select 'Heatmap Targets'
      - Entering a list of features seperated by commas will override the heatmap to show the features specified instead of the top features
    - Select 'Enable Feature Grouping'
      - This will allow you to Click the 'Browse' button next to the checkbox
      - Click the 'Browse' button to load a Feature-Group Map
        - Select a csv file from the pop up
          - The first row of the csv file should be, 'Feature,Group'
          - Every other row should contain a Feature in the first column and it's associated group in the second column
          - Any Features not in the Feature-Group Map will be assigned their own individual group automatically
      - Groups Features together to use the same color on the Biplot and Interactive Biplot

5. **Save Plot**
    - Below the 'PCA Analysis Results' box should be text showing the current output directory. By defualt: KUpca_plots_output
    - Click the 'Select Output Directory' button to the right of the text to select a different ouput directory.
    - Click the 'Save Plot' button to save a .png file of the currently displayed plot to the output directory


## Development Notes

### For updating:

- `app.py` is the GUI control hub  
    
- `pca.py` contains logic for dimension reduction and variance calculation
    
- Constants (e.g., styling and color palettes) are stored in `constant.py`
    

### Technical Notes

- Interactive plots use `plotly` (check dependencies)
- Color grouping maps must be CSVs with valid column-to-group mappings