# constants.py
OUTPUT_DIR = 'KUpca_plots_output'

FEATURE_GROUPS_COLORS = {
    "FAB": "black",
    "non-FAB": "silver",
    "non-RAA pests": "pink",
    "Beneficials": "green",
    "RAA": "red"
}

DEFAULT_COLUMNS_TO_DROP = [
    'Site', 'SampleNum', 'Type', 'farm', 'EventId', 'SampleID',
    'trees.assessed', 'flower.clusters.assessed', 'Year', 'treat',
    'Rep', 'SideFlowerStrip', 'SideFlowerStrip_E',
    'SideFlowerStrip_W', 'SideFlowerStrip_preflow'
]

LABEL_STYLE = {
    "font":   ('Helvetica', 10),
    "bg":     "#f5f5f5",

}

# Style constants
BUTTON_STYLE = {
    'font': ('Helvetica', 10),
    'bg': '#007ACC',
    'fg': 'white',
    'activebackground': '#005f99',
    'relief': 'raised',
    'width': 18
}

COLOR_PALETTES = {
    "Default": {
        "FAB": "black",
        "non-FAB": "silver",
        "non-RAA pests": "pink",
        "Beneficials": "green",
        "RAA": "red"
    },
    "Colorblind-Friendly": {
        "FAB": "#117733",
        "non-FAB": "#88CCEE",
        "non-RAA pests": "#CC6677",
        "Beneficials": "#DDCC77",
        "RAA": "#332288"
    },
    "Bright": {
        "FAB": "#FF0000",
        "non-FAB": "#00FF00",
        "non-RAA pests": "#0000FF",
        "Beneficials": "#FFFF00",
        "RAA": "#FF00FF"
    }
}