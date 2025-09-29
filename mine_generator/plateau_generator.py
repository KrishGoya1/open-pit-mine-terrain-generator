# mine_generator/plateau_generator.py
"""
Plateau generator by reusing pit generation logic.
We generate a pit, flip it vertically, scale it down, and offset it
to create a dump/plateau feature.
"""

from . import config as cfg
from . import pit_generator


def compute_plateau_height_at(x, y):
    """
    Compute plateau height at (x, y) by reusing pit depth generation.
    Returns None if plateau is disabled.
    """
    if not cfg.PLATEAU_ENABLED:
        return None

    # Local coords relative to plateau center
    lx, ly = x - cfg.PLATEAU_CENTER_X, y - cfg.PLATEAU_CENTER_Y

    # Get pit depth at this local point
    pit_depth = pit_generator.compute_pit_depth(lx, ly)

    # Flip sign (pit is negative, plateau should be positive)
    plateau_h = -pit_depth

    # Scale plateau height down
    plateau_h *= cfg.PIT_DEPTH_VARIATION  # or a custom factor, e.g. 0.6

    # Clamp to plateau max height
    if plateau_h > cfg.PLATEAU_MAX_HEIGHT:
        plateau_h = cfg.PLATEAU_MAX_HEIGHT

    # Ensure plateau only within radius
    if (lx**2 + ly**2) ** 0.5 > cfg.PLATEAU_RADIUS:
        return None

    return plateau_h
