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
    │   ├── biplot_box.py           ← GUI functionality for creating several types of plots
    │   ├── heatmap_box.py          ← GUI functionality for generating a heatmap
    │   ├── load_clean_file_box.py  ← GUI functionality for loading and cleaning data
    │   └── visual_settings_box.py  ← GUI functionality for selecting parameters for generating plots
    │
    └── utils/
        ├── constant.py             ← Styling and Theme 
        └── file_operations.py      ← CSV loading/saving utilities
```

## How to start the application

- To run on Linux
  - Clone the repository, ```git clone https://github.com/wiscbicklab/PCA_11.27.24.git```
  - Open the repository, ```cd PCA_11.27.24```
  - Create a virtual enviroment, ```python -m venv NAME_OF_ENVIROMENT```
  - Activate the enviroment, ```source NAMEOF_ENVIROMENT/bin/activate```
  - Install dependencies, ```pip install adjustText chardet matplotlib numpy pandas plotly scikit-learn seaborn Screeninfo```
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

3. **Configure Settings**:
    
    - Select a target variable. Options: None, BBCH, and custom target
      - Determines how the points will be color coded for the PCA plot
      - If Custom target is selected you must enter the target you want to use in the box below
      - If Custom target is selected and the custom target isn't found in the data None is used
    - Select the 'Number of PCA components'
      - Determines the number of PCA components shown on the Scree Plot and heatmap
    - Select the 'Number of Features'
      - If Feature Grouping is not enabled this determines the number of features to show on the biplot and interactive biplot
      - Determines the number of features to use for the 'Top Feature Loadings' plot
      - If 'Top Features' is selected for the heatmap mode this determines the number of features to use in the heatmap
    - Select the "Focused PCA Component"
      - This determines the PCA component to sort Loadings by for both the "Top Feature Loadings' plot and heatmap
    - Select the 'Text Distance for Labels'
      - This is a value that changes where the labels are placed on the biplot.
      - Only Change this if you are having issues with text label overlap

3. **Generate Plots**:
    - Click the 'Visualize PCA' button to create a visualization of all points in the first two Principle Components
    - Click the 'Show Scree Plot' button to generate a scree plot with the PCA results
    - Click the 'Biplot' button to generate a Biplot over the first two Principle Components
    - Click the 'Interactive Biplot' button to generate an interactive biplot. This will be saved as an html file and opened in your browser
    - Click the 'Top Feature Loadings' button to generate a bar plot of the absolute loadings. Sorted by top values on the selected PCA component

5. **Enable Feature Grouping**
    - Click the 'Enable Feature Grouping' checkbox at the top of the plot generation box
    - Click the 'Browse' button next to the 'Feature Grouping Map:' text
    - Select a csv file from the pop up
      - The first row of the csv file should be, 'Feature,Group'
      - Every other row should contain a Feature in the first column and it's associated group in the second column
      - Extra Features not found in the dataset are fine
    - Click on the 'Biplot' or 'Interactive Biplot' buttons to generate new plots color coded by group instead of feature

6. **Generate Heatmap**
    - Select the heatmap feature from the dropdown menu or select 'Custom Features
      - If 'Custom Features' is selected type the feature you would like to see in the box below seperated by commas
    - Click the 'Plot Heatmap' button to generate a heatmap.

7. **Save Plot**
    - Below the 'PCA Analysis Results' box should be text showing the current output directory. By defualt: KUpca_plots_output
    - Click the 'Select Output Directory' button to the right of the text to select a different ouput directory.
    - Click the 'Save Plot' button to save a .png file of the currently displayed plot to the output directory

8. **Select Color Palette**
    - At the botton of the left side of the application is a dropdown that allows you to change the color palette used for the Biplot and Interactive Biplot
    - This color palette applies colors to the following groupings: fab, non-fab, non-raa pests, beneficials, and raa.
    - For any other groups or features a color-blind friendly palette is used if 10 or less are being used
      If more than 10 but 20 or less are being used a non-color-blind palette is used

## Development Notes

### For updating:

- `app.py` is the GUI control hub  
    
- `pca.py` contains logic for dimension reduction and variance calculation
    
- Constants (e.g., styling and color palettes) are stored in `constant.py`
    

### Technical Notes

- Interactive plots use `plotly` (check dependencies)
- Color grouping maps must be CSVs with valid column-to-group mappings