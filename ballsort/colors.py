import colorsys

def generate_kivy_colors(num_colors):
    """
    Generates a list of distinct RGB tuples for Kivy.
    The colors have high saturation and value to appear vibrant.
    """
    colors = []
    for i in range(num_colors):
        hue = i / float(num_colors)
        # Offset to spread colors nicely, avoid super dark
        r, g, b = colorsys.hsv_to_rgb(hue, 0.85, 0.95)
        # Kivy uses [0, 1] for RGB
        colors.append((r, g, b, 1.0))
    return colors
