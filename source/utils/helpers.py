import matplotlib.cm as cm
import matplotlib.colors as mcolors

def generate_color_palette(n_groups, preferred_colors=None):
    """
    Generate a color palette for feature groups.

    Parameters:
    -----------
    n_groups : int
        The number of feature groups to generate colors for.
    preferred_colors : dict, optional
        A dictionary of predefined colors for specific feature groups. Keys are group names, and values are color codes.

    Returns:
    --------
    dict
        A dictionary where keys are feature group names (e.g., "Group 1", "FAB") and values are color codes (hex).
    """
    # Define default preferred colors if not provided
    if preferred_colors is None:
        preferred_colors = {
            "FAB": "#000000",  # Black
            "non-FAB": "#C0C0C0",  # Silver
            "RAA": "#FF0000",  # Red
            "Beneficials": "#008000",  # Green
            "non-RAA pests": "#FFC0CB"  # Pink
        }

    # Generate a colormap for any additional groups beyond preferred colors
    num_extra_colors = max(0, n_groups - len(preferred_colors))
    colormap = cm.get_cmap('tab20', num_extra_colors)  # Use a 20-color palette
    extra_colors = [mcolors.rgb2hex(colormap(i)[:3]) for i in range(num_extra_colors)]

    # Combine preferred colors with extra colors
    all_colors = list(preferred_colors.values()) + extra_colors

    # Create a dictionary for all groups
    color_palette = {}
    for i in range(n_groups):
        group_name = f"Group {i+1}"  # Generic group name
        if i < len(preferred_colors):
            group_name = list(preferred_colors.keys())[i]  # Use predefined names if available
        color_palette[group_name] = all_colors[i]

    return color_palette