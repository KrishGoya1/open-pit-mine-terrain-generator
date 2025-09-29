# mine_generator/dump_generator.py
"""
Handles the generation of overburden dumps around the mine pit.
"""
import math

from . import config as cfg
from . import utils
from . import pit_generator  # Depends on pit_generator for rim location

def _angle_diff(a, b):
    """Calculates the shortest angle difference between two angles in radians."""
    return (a - b + math.pi) % (2.0 * math.pi) - math.pi

def build_dump_sectors():
    """Defines the angular sectors where dumps will be placed."""
    sectors = []
    # Main dumps
    for _ in range(cfg.DUMP_MAIN_COUNT):
        if cfg.rng_global.random() < cfg.DUMP_PLACEMENT_BIAS:
            ang = cfg.WORKING_FACE_ANGLE + cfg.rng_global.uniform(-math.radians(30), math.radians(30))
        else:
            ang = cfg.rng_global.uniform(-math.pi, math.pi)
        halfw = math.radians(cfg.DUMP_MAIN_SECTOR_DEG * 0.5 * cfg.rng_global.uniform(0.9, 1.1))
        maxh = cfg.DUMP_MAX_HEIGHT * cfg.rng_global.uniform(0.85, 1.12)
        extent = cfg.DUMP_EXTENT * cfg.rng_global.uniform(0.8, 1.15)
        sectors.append((ang, halfw, maxh, extent, 1.0))

    # Small dumps
    for _ in range(cfg.DUMP_SMALL_COUNT):
        ang = cfg.rng_global.uniform(-math.pi, math.pi)
        halfw = math.radians(cfg.DUMP_SMALL_SECTOR_DEG * 0.5 * cfg.rng_global.uniform(0.6, 1.1))
        maxh = cfg.DUMP_MAX_HEIGHT * cfg.rng_global.uniform(0.20, 0.65)
        extent = cfg.DUMP_EXTENT * cfg.rng_global.uniform(0.45, 0.9)
        sectors.append((ang, halfw, maxh, extent, 0.6))
    return sectors

DUMP_SECTORS = build_dump_sectors()

def _dump_height_from_sector(x, y, sector):
    """Calculates height contribution for a single dump sector."""
    center_angle, halfw, maxh, extent, weight = sector
    r, theta = math.hypot(x, y), math.atan2(y, x)
    
    eff_r = pit_generator.compute_effective_radius(theta)
    dist_out = r - eff_r
    if dist_out <= 0.0 or dist_out > extent:
        return -9e9

    d_ang = _angle_diff(theta, center_angle)
    ang_fall = utils.smoothstep(1.0 - (abs(d_ang) / halfw)) if abs(d_ang) < halfw else 0.0
    if ang_fall <= 0.0:
        return -9e9

    tan_repose = math.tan(math.radians(cfg.DUMP_ANGLE_OF_REPOSE))
    max_allowed_by_repose = dist_out * tan_repose
    effective_maxh = min(maxh, max_allowed_by_repose)
    
    bench_w = max(cfg.DUMP_MIN_BENCH_WIDTH, (cfg.DUMP_BENCH_HEIGHT / max(1e-6, tan_repose)))
    bench_count = int(math.ceil(extent / bench_w))
    bench_idx = max(0, min(bench_count - 1, int(dist_out / bench_w)))
    base_elev = (bench_idx + 1) / float(max(1, bench_count)) * effective_maxh
    
    n = utils.fbm(math.cos(theta)*0.9 + bench_idx*0.21, math.sin(theta)*0.9 + bench_idx*0.24, cfg.NOISE_SEED + bench_idx*7, octaves=2)
    p = (n * 0.5 + 0.5)
    skip = 1.0
    if p > 0.65:
        severity = max(0.0, min(1.0, (p - 0.65) / (1.0 - 0.65)))
        skip = utils.lerp(1.0, 0.25, utils.smoothstep(severity))
    
    noise_elev = utils.fbm((x + 123.4)*0.02, (y - 91.2)*0.02, cfg.NOISE_SEED + 19 + bench_idx, octaves=3) * (cfg.DUMP_NOISE_VARIATION * 0.5)
    
    elev = base_elev * skip + noise_elev
    
    fall_t = utils.smoothstep(1.0 - (dist_out / extent))
    elev *= fall_t * ang_fall * weight
    
    elev = max(0.0, min(elev, dist_out * tan_repose))
    return elev * cfg.VERTICAL_SCALE

def compute_dump_height_at(x, y):
    """Finds the maximum dump height from all defined sectors at a point."""
    heights = [_dump_height_from_sector(x, y, s) for s in DUMP_SECTORS]
    best = max(heights)
    return best if best > -1e8 else None