import colorsys

# Sasha Trubetskoy's 20 distinct colors for maximum categorical contrast
DISTINCT_COLORS_RGB255 = [
    (230, 25, 75),    # Red
    (60, 180, 75),    # Green
    (255, 225, 25),   # Yellow
    (67, 99, 216),    # Blue
    (245, 130, 49),   # Orange
    (145, 30, 180),   # Purple
    (66, 212, 244),   # Cyan
    (240, 50, 230),   # Magenta
    (191, 239, 69),   # Lime
    (250, 190, 212),  # Pink
    (70, 153, 144),   # Teal
    (220, 190, 255),  # Lavender
    (154, 99, 36),    # Brown
    (255, 250, 200),  # Beige
    (128, 0, 0),      # Maroon
    (170, 255, 195),  # Mint
    (128, 128, 0),    # Olive
    (255, 216, 177),  # Apricot
    (0, 0, 117),      # Navy
    (169, 169, 169)   # Grey
]

def generate_kivy_colors(num_colors):
    """
    Returns a slice of expertly crafted high-contrast Kivy colors [0, 1].
    Falls back to dynamic HSV generation if pushed beyond the known 20 colors.
    """
    colors = []
    
    # Use the highly distinct colors first
    for i in range(min(num_colors, len(DISTINCT_COLORS_RGB255))):
        r, g, b = DISTINCT_COLORS_RGB255[i]
        colors.append((r / 255.0, g / 255.0, b / 255.0, 1.0))
        
    # Fallback safety net if somehow requested > 20
    remaining = num_colors - len(DISTINCT_COLORS_RGB255)
    if remaining > 0:
        for i in range(remaining):
            hue = i / float(remaining)
            r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
            colors.append((r, g, b, 1.0))
            
    return colors
