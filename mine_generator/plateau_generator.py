# mine_generator/plateau_generator.py
"""
Plateau generator by reusing pit generation logic.
We generate a pit, flip it vertically, scale it down, and offset it
to create a dump/plateau feature.
"""

from . import config as cfg
from . import pit_generator

def compute_plateau_height_at(x, y):
    """Plateau as flipped pit with rim blending + flat top + pseudo roads."""
    if not cfg.PLATEAU_ENABLED:
        return None

    lx, ly = x - cfg.PLATEAU_CENTER_X, y - cfg.PLATEAU_CENTER_Y
    r, theta = math.hypot(lx, ly), math.atan2(ly, lx)

    if r > cfg.PLATEAU_RADIUS:
        return None

    # --- Base pit depth (flipped) ---
    pit_depth = pit_generator.compute_pit_depth(lx, ly)
    plateau_h = -pit_depth * 0.7

    # --- Top pad flattening ---
    if r < cfg.PLATEAU_TOP_PAD_RADIUS:
        pad_blend = utils.smoothstep(1.0 - (r / cfg.PLATEAU_TOP_PAD_RADIUS))
        plateau_h = utils.lerp(plateau_h, cfg.PLATEAU_MAX_HEIGHT, pad_blend * cfg.PLATEAU_TOP_FLATTEN)

    # --- Blend with rim ---
    rim_r = pit_generator.compute_effective_radius(theta)
    dist_from_rim = max(0.0, r - rim_r)
    blend_t = utils.smoothstep(1.0 - (dist_from_rim / (cfg.PLATEAU_RADIUS * 0.5)))
    plateau_h *= blend_t

    # --- Add pseudo-road spiral ---
    eff_r = pit_generator.compute_effective_radius(theta, use_road_smooth=False)
    spiral_theta = pit_generator.road_spiral_theta_from_radius(r, eff_r)
    d = (theta - spiral_theta + math.pi) % (2.0 * math.pi) - math.pi
    if abs(d) < math.radians(10):
        plateau_h *= cfg.ROAD_FLATTEN

    # --- Noise for realism ---
    noise = utils.fbm(
        x * 0.02, y * 0.02, cfg.NOISE_SEED + 2021, octaves=3
    ) * cfg.PLATEAU_NOISE_AMPLITUDE
    plateau_h += noise

    return max(0.0, min(plateau_h, cfg.PLATEAU_MAX_HEIGHT))
