# mine_generator/utils.py
"""
General-purpose utility functions for math and noise generation.
"""
from mathutils import Vector, noise

def perlin3(x, y, z):
    """3D Perlin noise lookup."""
    return noise.noise(Vector((x, y, z)))

def fbm(x, y, seed, octaves=4, lacunarity=2.0, gain=0.5):
    """Fractional Brownian Motion (FBM) noise function."""
    value = 0.0
    freq = 1.0
    amp = 1.0
    for _ in range(octaves):
        value += amp * perlin3(x * freq, y * freq, seed)
        freq *= lacunarity
        amp *= gain
    return value

def smoothstep(t):
    """A smooth interpolation function."""
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def lerp(a, b, t):
    """Linear interpolation between two values."""
    return a + (b - a) * t