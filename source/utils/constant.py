FEATURE_GROUPS_COLORS = {
    "FAB": "black",
    "non-FAB": "silver",
    "non-RAA pests": "pink",
    "Beneficials": "green",
    "RAA": "red"
}

DEFAULT_COLUMNS_TO_DROP = [
    "Site", "SampleNum", "Type", "farm", "EventId", "SampleID",
    "trees.assessed", "flower.clusters.assessed", "Year", "treat",
    "Rep", "SideFlowerStrip", "SideFlowerStrip_E",
    "SideFlowerStrip_W", "SideFlowerStrip_preflow"
]

BG_COLOR = {"bg": "#f5f5f5",}

# Style constants
LABEL_STYLE = {
    "font":   ("Helvetica", 10),
    "bg":     BG_COLOR["bg"],
}
BANNER_STYLE = {
    "font": ("Helvetica", 12),
    "bg": "#dcdcdc",
    "relief": "groove",
}
BUTTON_STYLE = {
    "font": ("Helvetica", 10),
    "bg": "#007ACC",
    "fg": "white",
    "activebackground": "#005f99",
    "relief": "raised",
    "width": 22,
}
OPTION_MENU_STYLE = {
    "font": ("Helvetica", 10),
    "bg": "#007ACC",
    "fg": "white",
    "activebackground": "#005f99",
    "relief": "raised",
    "width": 20,
}
RAD_BUTTON_STYLE = {
    "font": ("Helvetica", 10),
    "bg": "#e8e8e8",
    "fg": "black",
    "activebackground": "#d0d0d0",
}
ENTRY_STYLE = {
    "font": ("Helvetica", 10),
    "bg": "white",
    "width": 22
}



COLOR_PALETTES = {
    "Default": {
        "fab": "black",
        "non-fab": "silver",
        "non-raa pests": "pink",
        "beneficials": "green",
        "raa": "red"
    },
    "Colorblind-Friendly": {
        "fab": "#117733",
        "non-fab": "#88CCEE",
        "non-raa pests": "#CC6677",
        "beneficials": "#DDCC77",
        "raa": "#332288"
    },
    "Bright": {
        "fab": "#FF0000",
        "non-fab": "#00FF00",
        "non-raa pests": "#0000FF",
        "beneficials": "#FFFF00",
        "raa": "#FF00FF"
    }
}