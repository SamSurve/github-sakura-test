"""
Theme and styling constants for Sakura GitHub Contributions PNG visualization.
"""

# Canvas Dimensions
CANVAS_WIDTH = 1200
CANVAS_HEIGHT = 350

# Color Palette
BG_COLOR = "#FCF8FA"         # Clean white with subtle warm pink undertone
BORDER_COLOR = "#1A1A1A"     # Crisp elegant black border
INNER_BORDER_COLOR = "#ECDCE4" # Subtle inner border
TEXT_COLOR = "#222222"       # High-contrast primary dark text
TEXT_MUTED = "#776677"       # Soft muted plum for labels and dates
ACCENT_PINK = "#E84C8F"      # Vibrant Sakura pink accent

# 5 Pink Contribution Levels (Less -> More)
CONTRIBUTION_COLORS = [
    "#FDF6F8",  # Level 0: Pure pale Sakura snow (empty/zero contributions)
    "#FBC4D6",  # Level 1: Soft delicate petal
    "#F58EB7",  # Level 2: Vibrant cherry blossom
    "#E84C8F",  # Level 3: Deep rich Sakura magenta
    "#C11E66"   # Level 4: Crimson Sakura dusk (maximum contributions)
]

# GitHub Contribution Level Mapping
LEVEL_MAP = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4
}

# Heatmap Grid Layout
GRID_START_X = 265
GRID_START_Y = 125
CELL_SIZE = 13
CELL_GAP = 3
CELL_RADIUS = 3

# Weekdays to display (1=Mon, 3=Wed, 5=Fri)
DISPLAY_WEEKDAYS = {
    1: "Mon",
    3: "Wed",
    5: "Fri"
}
