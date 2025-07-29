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
    "width": 28
}
SMALL_ENTRY_STYLE = {
    **ENTRY_SYLE,
    "width": 14
}

# Leftovers from previous build
DEFAULT_COLUMNS_TO_DROP = [
    "Site", "SampleNum", "Type", "farm", "EventId", "SampleID",
    "trees.assessed", "flower.clusters.assessed", "Year", "treat",
    "Rep", "SideFlowerStrip", "SideFlowerStrip_E",
    "SideFlowerStrip_W", "SideFlowerStrip_preflow"
]

