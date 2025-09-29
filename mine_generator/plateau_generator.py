# mine_generator/plateau_generator.py
"""
Handles the procedural generation of a standalone, terraced plateau
or overburden dump mountain.
"""
import math

# Import from our own package
from . import config as cfg
from . import utils

def compute_plateau_height_at(x, y):
    """
    Calculates the height of the plateau at a given (x, y) coordinate.
    Returns the height value or None if the point is outside the plateau's radius.
    """
    # If the feature is disabled in the config, do nothing.
    if not cfg.PLATEAU_ENABLED:
        return None

    # Calculate the distance of the point from the plateau's center
    lx = x - cfg.PLATEAU_CENTER_X
    ly = y - cfg.PLATEAU_CENTER_Y
    r = math.hypot(lx, ly)

    # If the point is outside the base of the plateau, do nothing.
    if r > cfg.PLATEAU_RADIUS:
        return None

    # --- Calculate the Plateau Shape ---

    height = 0.0
    # Case 1: The point is on the flat top of the plateau
    if r <= cfg.PLATEAU_FLAT_TOP_RADIUS:
        height = cfg.PLATEAU_MAX_HEIGHT
    
    # Case 2: The point is on the sloped, terraced sides
    else:
        # Calculate how far we are along the slope (0.0 at the outer edge, 1.0 at the inner edge)
        slope_width = cfg.PLATEAU_RADIUS - cfg.PLATEAU_FLAT_TOP_RADIUS
        
        # Avoid division by zero if the plateau is a perfect cone
        if slope_width < 1e-6:
             return None
             
        t = (r - cfg.PLATEAU_FLAT_TOP_RADIUS) / slope_width
        
        # Invert t so that it's 1.0 at the top and 0.0 at the bottom
        t_inv = 1.0 - t
        
        # Calculate the ideal height on a smooth slope
        smooth_height = t_inv * cfg.PLATEAU_MAX_HEIGHT
        
        # Create terraced benches by "stepping" the height
        num_benches = math.floor(cfg.PLATEAU_MAX_HEIGHT / cfg.PLATEAU_BENCH_HEIGHT)
        step = t_inv * num_benches
        
        # The final height is based on which bench we are on
        height = math.floor(step) * cfg.PLATEAU_BENCH_HEIGHT

    # Add surface noise for realism
    noise_val = utils.fbm(x * 0.04, y * 0.04, cfg.NOISE_SEED + 101, octaves=4)
    height += noise_val * cfg.PLATEAU_NOISE_AMPLITUDE

    # Ensure height is not negative and apply vertical scaling
    return max(0.0, height) * cfg.VERTICAL_SCALE