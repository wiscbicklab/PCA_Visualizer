
```text
PCA_11.27.24-pca/
│
├── requirements.txt ← Python dependencies
│
└── source/
├── analysis/
│ └── pca.py ← Core PCA computation
├── gui/
│ ├── app.py ← Main GUI application (tkinter)
│ └── spillover.py ← Event bindings & interactivity helpers
├── utils/
│ ├── constant.py ← Column/feature definitions, defaults
│ ├── file_operations.py ← CSV loading/saving utilities
│ └── helpers.py ← Data cleaning, transformation utilities
└── visualization/
├── base.py ← Plotting foundation
├── biplot.py ← PCA biplot rendering
└── heatmap.py ← Heatmap rendering
```

**For updating:**

- `app.py` is the GUI control hub....  
  -- to run and debug from IDE by hitting run,  add the following to  bottom of app.py
  
  if __name__ == "__main__":  
    root = tk.Tk()  
    app = PCAAnalysisApp(root)  
    root.mainloop()
    
- `pca.py` contains logic for dimension reduction and variance calculation.
    
- Would be worth extending plotting capabilities in `biplot.py` and `heatmap.py`.
    
- Constants (e.g., feature groups, default columns to drop) are stored in `constant.py`.

**Other Notes**
- Interactive plots use `plotly` (check dependencies).
- Color grouping maps must be CSVs with valid column-to-group mappings.
- Filtering BBCH values is case-sensitive: ensure data uses formats like `"B69"`.

-----------------------------------------------------
**Overview of Existing GUI Methods:** 

- **Load a CSV file**
    - Use the file browser to choose a dataset.
        
- **Clean and Filter Data**
    - Handle missing values (mean, median, 0, or null).
    - Filter by specific BBCH growth stages (B59, B69, B85)
	    *** this is relevant to the KU team/data Emily was working with 
    - Drop unwanted columns
        
- **Run PCA (Principal Component Analysis)**
    
    - Select how many components to extract.
    - Choose how many top features to display in the biplot.
	    - currently diff group colors are not picking so it's greyed out - this needs fixing!
    - Label axes based on a target variable (if desired).
	    - - PCA reduces the dimensionality of your data based only on the numerical features you specify — the **target variable is not included** in this reduction.
	    - However, when you visualize the results (e.g., with a biplot), the **target variable is used to color the data points**, allowing you to see how different classes or groups are distributed in the reduced PCA space.
	    
- **Visualize Results**
    
    - View scree plots.
    - Generate standard or grouped biplots (colored by label or cluster).
    - Plot heatmaps of top PCA-contributing features.
        
- **Save Outputs**
    - Cleaned CSV
    - Scree plot, biplot, heatmap (static and/or interactive)
      
----------------------

**Steps to test workflow of current GUI:** 

1) go to this link:

[https://github.com/wiscbicklab/PCA_11.27.24/releases/tag/pca](https://github.com/wiscbicklab/PCA_11.27.24/releases/tag/pca "https://github.com/wiscbicklab/pca_11.27.24/releases/tag/pca")

2) download:

KUPCA_GUI.exe

3) open from browser's downloads (you'll have to override - your laptop likely won't trust - so you'll have to select something like 'run anyway' or rightclick and run as administrator)

4) make the window as big as possible - the default will have a sort of smooshed-down look

this was GUI designed for files from: KUPCA_112724 (attached)

1) upload the data via browse: open USE_THIS_updated_encoded_cleaned_SC_all_BBCH_final.csv

2) be sure to drop the columns I included in the 'columns to drop' file - just copy/paste what is in A1

3) if you only want to look at a particular bbch stage of data you can filter to just that stage on the GUI by selecting the stage

4) hit Clean CSV 

5) the default setting will only show the 10 most significant features - you can change that number if you want more than 10 shown on the plot 

6) Run PCA then Visualize PCA (currently diff group colors are not picking so it's greyed out - trying to sort why right now)

7) ideally mapping feature would work - so you could load the KUPCA_featuregroups csv and it handles it for you -  but my logic isn't picking something up. 

8) run the biplot with groups function - this is working for exploratory purposes - I have been spending more time with the interactive plotting for the purposes of this app but it won't be worth your time for this conversation. 

9) you can check the top loadings button to see ranking of features

10) if you want to run the scree plot with more than 2 PC - you'll have to adjust that component number textbox from 2 (I set that to the default) and then run PCA again. 

11) ignore heatmap  - it's not showing top features - it's showing the index of features.

-----------------------------------------------------------------------
**Flagged Issues/missing logic:** 
1) Visualize PCA - currently diff group colors are not picking so it's greyed out - needs fixing 
2) Mapping Feature - logic enable/disabling this isn't do anything - needs fixing
3) Heatmap - showing index of features - update this logic so showing the top features 

