# constants.py
OUTPUT_DIR = 'KUpca_plots_output5'

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