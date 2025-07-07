BG_COLOR = {"bg": "#f5f5f5",}
FONT = {"font":   ("Helvetica", 10)}

# Style constants
LABEL_STYLE = {
    **FONT,
    **BG_COLOR,
}
BANNER_STYLE = {
    "font": ("Helvetica", 12),
    "bg": "#dcdcdc",
    "relief": "groove",
}
BUTTON_STYLE = {
    **FONT,
    "bg": "#007ACC",
    "fg": "white",
    "activebackground": "#005f99",
    "relief": "raised",
    "width": 22,
}
OPTION_MENU_STYLE = {
    **FONT,
    "bg": "#007ACC",
    "fg": "white",
    "activebackground": "#005f99",
    "relief": "raised",
    "width": 20,
}
RAD_BUTTON_STYLE = {
    **FONT,
    "bg": "#e8e8e8",
    "fg": "black",
    "activebackground": "#d0d0d0",
}
ENTRY_SYLE = {
    **FONT,
    "bg": "white",
}
BIG_ENTRY_STYLE = {
    **ENTRY_SYLE,
    "width": 22
}
SMALL_ENTRY_STYLE = {
    **ENTRY_SYLE,
    "width": 14
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

# Leftovers from previous build
DEFAULT_COLUMNS_TO_DROP = [
    "Site", "SampleNum", "Type", "farm", "EventId", "SampleID",
    "trees.assessed", "flower.clusters.assessed", "Year", "treat",
    "Rep", "SideFlowerStrip", "SideFlowerStrip_E",
    "SideFlowerStrip_W", "SideFlowerStrip_preflow"
]

