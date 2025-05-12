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

DEFAULT_STYLE = {
    "label_font":   ('Helvetica', 10),
    "bg_color":     "#f5f5f5",

}