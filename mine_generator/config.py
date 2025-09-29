# mine_generator/config.py
"""
Central configuration file for the procedural mine generator.
All user-tunable parameters are located here.
"""
import math
import random

# ---------------------- USER-TUNABLE PARAMETERS ----------------------
RESOLUTION = 220
SIZE = 320.0

# Pit geometry
MAX_PIT_RADIUS = 110.0
MAX_DEPTH = 60.0
BENCH_HEIGHT = 6.0
MIN_BENCH_WIDTH = 8.0
MEAN_BENCH_WIDTH = 12.0

# Road & ramps
ROAD_WIDTH = 12.0
ROAD_SPIRAL_TURNS = 4.5
ROAD_FLATTEN = 0.60
BRANCH_RAMP_COUNT = 3
SECONDARY_RAMP_COUNT = 4
BRANCH_ANGLE_SPREAD = math.radians(36)
BRANCH_LENGTH_FACTOR = 0.40
SECONDARY_RAMP_ARC = math.radians(24)
SECONDARY_RAMP_LENGTH = 0.55

# Bottom working pad
BOTTOM_PAD_RADIUS = 30.0
PAD_DEPTH_FACTOR = 0.98

# Bench skips
BENCH_SKIP_PROBABILITY = 0.18
BENCH_SKIP_REDUCTION = 0.12

# Noise / FBM fields
NOISE_SEED = None  # Set to an integer for a fixed seed, or None for random
NOISE_LOW_SCALE = 0.006
NOISE_LOW_AMPL = 1.8
NOISE_MED_SCALE = 0.02
NOISE_MED_AMPL = 0.6
NOISE_HIGH_SCALE = 0.08
NOISE_HIGH_AMPL = 0.18
MICRO_AMPL = 0.12

# Radial boundary deformation params
BOUNDARY_NOISE_SCALE = 0.95
BOUNDARY_NOISE_STRENGTH = 0.10
BOUNDARY_FBM_OCTAVES = 3
BOUNDARY_PER_BENCH_VARIATION = 0.18

# Center-preservation params
INNER_STEP_PRESERVE = 0.45
CENTER_JITTER_REDUCTION = 0.18
CENTER_SKIP_REDUCTION = 0.65

# Road smoothing for boundary
ROAD_BOUNDARY_SMOOTH = 0.70

# MULTI-PIT / nested pit parameters
MULTI_PIT_COUNT = 2
PIT_SPREAD = 38.0
PIT_SIZE_VARIATION = 0.65
PIT_DEPTH_VARIATION = 0.55
EXPLICIT_PIT_CENTERS = None  # e.g., [(0, 0, 1.0, 1.0), (40, 10, 0.7, 0.8)]

# DUMP (overburden) parameters
DUMP_MAIN_COUNT = 1
DUMP_SMALL_COUNT = 3
DUMP_MAIN_SECTOR_DEG = 90.0
DUMP_SMALL_SECTOR_DEG = 36.0
DUMP_MAX_HEIGHT = 26.0
DUMP_BENCH_HEIGHT = 4.5
DUMP_MIN_BENCH_WIDTH = 6.0
DUMP_ANGLE_OF_REPOSE = 34.0
DUMP_EXTENT = 130.0
DUMP_NOISE_VARIATION = 0.9
DUMP_PLACEMENT_BIAS = 0.65

# Erosion & smoothing
EROSION_ITERATIONS = 6
EROSION_RATE = 0.42

# Vertical compression
VERTICAL_SCALE = 0.55

# Mesh cleanup
MERGE_DIST = 1e-4
SUBDIVIDE_SMOOTH = True
SUBDIV_LEVELS = 1
APPLY_VERTEX_COLORS = True

# ---------------------- DERIVED & RANDOMIZED SETTINGS ----------------------
if NOISE_SEED is None:
    NOISE_SEED = random.randint(0, 2**30)
random.seed(NOISE_SEED)
rng_global = random.Random(NOISE_SEED)

# The angle determining the main road's position relative to the working face
WORKING_FACE_ANGLE = rng_global.uniform(-math.pi, math.pi)