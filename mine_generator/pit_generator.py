# mine_generator/pit_generator.py
"""
Handles the procedural generation of the open-pit mine geometry,
including benches, roads, ramps, and multi-pit blending.
"""
import math
import random

# Import from our own package
from . import config as cfg
from . import utils

def generate_pit_centers():
    """Generates the locations and scales of all pits, including the main one."""
    if cfg.EXPLICIT_PIT_CENTERS:
        return [(c[0], c[1], float(c[2]), float(c[3])) for c in cfg.EXPLICIT_PIT_CENTERS]
    
    centers = [(0.0, 0.0, 1.0, 1.0)]  # Main pit
    for i in range(cfg.MULTI_PIT_COUNT):
        ang = cfg.rng_global.uniform(-math.pi, math.pi)
        dist = cfg.rng_global.uniform(cfg.PIT_SPREAD * 0.45, cfg.PIT_SPREAD * 1.25)
        cx = math.cos(ang) * dist
        cy = math.sin(ang) * dist
        size_mul = cfg.rng_global.uniform(cfg.PIT_SIZE_VARIATION, 1.0)
        depth_mul = cfg.rng_global.uniform(cfg.PIT_DEPTH_VARIATION, 1.0)
        centers.append((cx, cy, size_mul, depth_mul))
    return centers

PIT_CENTERS = generate_pit_centers()

# ... (Helper functions for benches, roads, ramps, etc.) ...
# [All functions from `total_bench_count` to `depth_at_for_center` go here]

def total_bench_count(depth_scale=1.0):
    return max(1, int((cfg.MAX_DEPTH * depth_scale) / cfg.BENCH_HEIGHT))

def bench_index_for_radius(r, effective_radius, depth_scale=1.0):
    total_steps = total_bench_count(depth_scale)
    norm = 1.0 - (r / effective_radius)
    norm = max(0.0, min(1.0, norm))
    return int(norm * total_steps)

def bench_horizontal_radius_for_index(idx, theta, size_scale=1.0):
    total_steps = total_bench_count(size_scale)
    t = idx / float(total_steps) if total_steps > 0 else 0.0
    base_radius = (1.0 - t) * cfg.MAX_PIT_RADIUS * size_scale
    perturb = utils.fbm(math.cos(theta) * 0.22 + idx * 0.13,
                  math.sin(theta) * 0.22 + idx * 0.19,
                  cfg.NOISE_SEED + idx * 9, octaves=2)
    width_jitter = (perturb * 0.5 + 0.5) * (cfg.MEAN_BENCH_WIDTH - cfg.MIN_BENCH_WIDTH)
    r_base = base_radius + width_jitter + (idx * 0.01)
    
    sx = math.cos(theta) * cfg.BOUNDARY_NOISE_SCALE
    sy = math.sin(theta) * cfg.BOUNDARY_NOISE_SCALE
    seed_for_bench = cfg.NOISE_SEED + int(idx * (cfg.BOUNDARY_PER_BENCH_VARIATION * 1000))
    noise_val = utils.fbm(sx, sy, seed_for_bench, octaves=cfg.BOUNDARY_FBM_OCTAVES)
    
    weight = utils.smoothstep(max(0.0, (t - 0.0) / 1.0))
    deformation = cfg.BOUNDARY_NOISE_STRENGTH * noise_val * weight
    
    r_distorted = max(0.1, r_base * (1.0 + deformation))
    return r_distorted

def radial_variation(theta):
    return utils.fbm(math.cos(theta) * 0.32, math.sin(theta) * 0.32, cfg.NOISE_SEED, octaves=3) * 0.48

def compute_effective_radius(theta, size_scale=1.0, use_road_smooth=True):
    base = cfg.MAX_PIT_RADIUS * size_scale
    broad = radial_variation(theta) * (cfg.MAX_PIT_RADIUS * 0.11 * size_scale)
    sx = math.cos(theta) * cfg.BOUNDARY_NOISE_SCALE
    sy = math.sin(theta) * cfg.BOUNDARY_NOISE_SCALE
    rim_noise = utils.fbm(sx, sy, cfg.NOISE_SEED + 3, octaves=cfg.BOUNDARY_FBM_OCTAVES)
    rim_deformation = rim_noise * (cfg.MAX_PIT_RADIUS * cfg.BOUNDARY_NOISE_STRENGTH * size_scale)
    eff = base + broad + rim_deformation
    
    if use_road_smooth:
        spiral_theta = road_spiral_theta_from_radius(eff, eff)
        d = (theta - spiral_theta + math.pi) % (2.0 * math.pi) - math.pi
        angle_abs = abs(d)
        angular_threshold = math.radians(18.0)
        if angle_abs < angular_threshold:
            blend = utils.smoothstep(1.0 - (angle_abs / angular_threshold))
            eff = utils.lerp(eff, base + broad, cfg.ROAD_BOUNDARY_SMOOTH * blend)
    return max(2.0, eff)

def road_spiral_theta_from_radius(r, effective_radius):
    frac = 1.0 - (r / effective_radius) if effective_radius != 0 else 0.0
    frac = max(0.0, min(1.0, frac))
    return cfg.WORKING_FACE_ANGLE + frac * (cfg.ROAD_SPIRAL_TURNS * 2.0 * math.pi)

def is_on_main_road(x, y, eff_r):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    if r > eff_r:
        return False, 0.0, 0.0
    spiral_theta = road_spiral_theta_from_radius(r, eff_r)
    d = (theta - spiral_theta + math.pi) % (2.0 * math.pi) - math.pi
    arc = abs(d) * max(1e-6, r)
    on = arc <= cfg.ROAD_WIDTH
    return on, arc

def branch_ramp_mask(x, y, eff_r):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    if r > eff_r:
        return 0.0
    rng = random.Random(int(cfg.NOISE_SEED) ^ 0xA5A5)
    base_angles = [rng.uniform(-math.pi, math.pi) for _ in range(cfg.BRANCH_RAMP_COUNT)]
    mask_val = 0.0
    for a in base_angles:
        d = (theta - a + math.pi) % (2.0 * math.pi) - math.pi
        if abs(d) < cfg.BRANCH_ANGLE_SPREAD:
            frac = 1.0 - (r / eff_r)
            branch_len = cfg.BRANCH_LENGTH_FACTOR + (utils.fbm(math.cos(a)*0.2, math.sin(a)*0.2, cfg.NOISE_SEED, octaves=2) * 0.12)
            if frac < branch_len:
                ang_fall = 1.0 - (abs(d) / cfg.BRANCH_ANGLE_SPREAD)
                mask_val = max(mask_val, ang_fall * (1.0 - (frac / branch_len)))
    return max(0.0, min(1.0, mask_val))

def secondary_ramp_mask(x, y, eff_r):
    r = math.hypot(x, y)
    theta = math.atan2(y, x)
    if r > eff_r:
        return 0.0
    rng = random.Random(int(cfg.NOISE_SEED) ^ 0x5EED)
    sec_angles = [rng.uniform(-math.pi, math.pi) for _ in range(cfg.SECONDARY_RAMP_COUNT)]
    mask_val = 0.0
    for a in sec_angles:
        d = (theta - a + math.pi) % (2.0 * math.pi) - math.pi
        if abs(d) < cfg.SECONDARY_RAMP_ARC:
            frac = 1.0 - (r / eff_r)
            if frac < cfg.SECONDARY_RAMP_LENGTH:
                ang_fall = 1.0 - (abs(d) / cfg.SECONDARY_RAMP_ARC)
                mask_val = max(mask_val, ang_fall * (1.0 - (frac / cfg.SECONDARY_RAMP_LENGTH)))
    return mask_val

def bench_skip_factor(idx, theta):
    n = utils.fbm(math.cos(theta)*0.7 + idx*0.19, math.sin(theta)*0.7 + idx*0.23, cfg.NOISE_SEED + idx*13, octaves=2)
    p = (n * 0.5 + 0.5)
    if p < cfg.BENCH_SKIP_PROBABILITY:
        return 1.0
    else:
        severity = (p - cfg.BENCH_SKIP_PROBABILITY) / (1.0 - cfg.BENCH_SKIP_PROBABILITY)
        severity = max(0.0, min(1.0, severity))
        return utils.lerp(1.0, cfg.BENCH_SKIP_REDUCTION, utils.smoothstep(severity))

def _depth_at_for_center(x, y, cx, cy, size_scale, depth_scale):
    """Internal function to calculate depth for a single pit center."""
    lx, ly = x - cx, y - cy
    r, theta = math.hypot(lx, ly), math.atan2(ly, lx)
    
    eff_r = compute_effective_radius(theta, size_scale)
    if r > eff_r:
        return utils.fbm((x + cx) * 0.0038, (y + cy) * 0.0038, cfg.NOISE_SEED + 21, octaves=4) * 1.2 * cfg.VERTICAL_SCALE * 0.6

    idx = bench_index_for_radius(r, eff_r, depth_scale)
    bench_depth = idx * cfg.BENCH_HEIGHT * depth_scale
    
    rim_radius = bench_horizontal_radius_for_index(idx, theta, size_scale)
    dist_to_rim = rim_radius - r
    edge_blur = max(1.0, cfg.MIN_BENCH_WIDTH * 0.5)
    edge_blend = utils.smoothstep((dist_to_rim + edge_blur) / edge_blur)
    
    on_road, arc = is_on_main_road(lx, ly, eff_r)
    if on_road:
        road_strength = utils.lerp(1.0, 0.0, min(1.0, arc / (cfg.ROAD_WIDTH * 1.3)))
        bench_depth *= utils.lerp(1.0, cfg.ROAD_FLATTEN, road_strength * (0.9 + 0.1 * size_scale))

    branch_mask = branch_ramp_mask(lx, ly, eff_r)
    if branch_mask > 1e-4:
        frac = 1.0 - (r / eff_r)
        ramp_strength = utils.smoothstep(frac) * branch_mask
        bench_depth *= utils.lerp(1.0, 0.38, ramp_strength * (0.8 + 0.2 * size_scale))

    sec_mask = secondary_ramp_mask(lx, ly, eff_r)
    if sec_mask > 1e-4:
        frac = 1.0 - (r / eff_r)
        ramp_strength = utils.smoothstep(frac) * sec_mask
        bench_depth *= utils.lerp(1.0, 0.50, ramp_strength * (0.8 + 0.2 * size_scale))

    skip = bench_skip_factor(idx, theta)
    preserve_weight = 0.0
    if eff_r > 0 and cfg.INNER_STEP_PRESERVE > 0:
        preserve_threshold = eff_r * cfg.INNER_STEP_PRESERVE
        if r < preserve_threshold:
            preserve_weight = 1.0 - (r / preserve_threshold)
            preserve_weight = max(0.0, min(1.0, preserve_weight))
    skip = utils.lerp(skip, 1.0, preserve_weight * (1.0 - cfg.CENTER_SKIP_REDUCTION))
    bench_depth *= skip

    if r < cfg.BOTTOM_PAD_RADIUS * size_scale:
        pad_depth = cfg.MAX_DEPTH * cfg.PAD_DEPTH_FACTOR * depth_scale
        pad_blend = utils.smoothstep(1.0 - (r / (cfg.BOTTOM_PAD_RADIUS * size_scale)))
        bench_depth = utils.lerp(bench_depth, pad_depth, pad_blend)

    jitter = utils.fbm((x + cx) * cfg.NOISE_MED_SCALE, (y + cy) * cfg.NOISE_MED_SCALE, cfg.NOISE_SEED + idx*11, octaves=3) * (cfg.BENCH_HEIGHT * 0.24)
    micro = utils.fbm((x + cx) * cfg.NOISE_HIGH_SCALE * 2.0, (y + cy) * cfg.NOISE_HIGH_SCALE * 2.0, cfg.NOISE_SEED + 97, octaves=2) * cfg.MICRO_AMPL
    
    if preserve_weight > 0.0:
        ease = utils.smoothstep(preserve_weight)
        jitter *= utils.lerp(cfg.CENTER_JITTER_REDUCTION, 1.0, (1.0 - ease))
        micro *= utils.lerp(cfg.CENTER_JITTER_REDUCTION, 1.0, (1.0 - ease))
    
    bench_depth += jitter * (1.0 - edge_blend) + micro * 0.5
    
    final_z = -max(0.0, min(cfg.MAX_DEPTH * depth_scale, bench_depth)) * cfg.VERTICAL_SCALE
    return final_z

def compute_pit_depth(x, y):
    """Computes the final pit depth by blending contributions from all pit centers."""
    depths = [_depth_at_for_center(x, y, cx, cy, size, depth) for cx, cy, size, depth in PIT_CENTERS]
    return min(depths) if depths else 0.0