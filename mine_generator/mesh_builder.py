# mine_generator/mesh_builder.py
"""
Handles all Blender-specific operations: creating the mesh grid,
applying vertex colors, and performing final mesh cleanup.
"""
import bpy
import bmesh

from . import config as cfg

def clear_scene():
    """Deletes all objects and mesh data from the current scene."""
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:
        bpy.data.meshes.remove(block)

def make_grid():
    """Creates the initial flat grid of vertices and faces."""
    verts, faces = [], []
    half = cfg.SIZE / 2.0
    step = cfg.SIZE / (cfg.RESOLUTION - 1)
    
    for v_y in range(cfg.RESOLUTION):
        y = -half + v_y * step
        for v_x in range(cfg.RESOLUTION):
            x = -half + v_x * step
            verts.append([x, y, 0.0])
            
    for v_y in range(cfg.RESOLUTION - 1):
        for v_x in range(cfg.RESOLUTION - 1):
            i = v_y * cfg.RESOLUTION + v_x
            a, b = i, i + 1
            c, d = i + cfg.RESOLUTION + 1, i + cfg.RESOLUTION
            faces.append((a, b, c, d))
            
    return verts, faces

def apply_erosion(z_grid):
    """Applies a simple hydraulic erosion simulation to a Z-height grid."""
    width = height = cfg.RESOLUTION
    offsets = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    for _ in range(cfg.EROSION_ITERATIONS):
        new_grid = z_grid.copy()
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                i = y * width + x
                zc = z_grid[i]
                neigh_sum = sum(z_grid[(y + dy) * width + (x + dx)] for dx, dy in offsets)
                neigh_avg = neigh_sum / len(offsets)
                delta = (neigh_avg - zc) * cfg.EROSION_RATE
                steep_proxy = abs(neigh_avg - zc)
                falloff = 1.0 / (1.0 + steep_proxy * 6.0)
                new_grid[i] = zc + delta * falloff
        z_grid = new_grid
    return z_grid

def _color_for_depth(z, zmin, zmax):
    """Determines vertex color based on normalized depth."""
    n = (zmax - z) / max(1e-6, (zmax - zmin))
    if n < 0.12: return (0.78, 0.75, 0.66, 1.0)  # Topsoil/Dumps
    elif n < 0.33: return (0.66, 0.56, 0.45, 1.0)
    elif n < 0.66: return (0.50, 0.48, 0.50, 1.0)
    else: return (0.18, 0.15, 0.12, 1.0)         # Deep rock

def add_vertex_colors(obj):
    """Applies vertex colors to the mesh based on Z-height."""
    me = obj.data
    zs = [v.co.z for v in me.vertices]
    zmin, zmax = min(zs), max(zs)
    
    col_layer = me.vertex_colors.new(name="StrataColor") if not me.vertex_colors else me.vertex_colors.active
    
    for poly in me.polygons:
        for loop_idx in range(poly.loop_start, poly.loop_start + poly.loop_total):
            v_idx = me.loops[loop_idx].vertex_index
            color = _color_for_depth(me.vertices[v_idx].co.z, zmin, zmax)
            col_layer.data[loop_idx].color = color

def build_mesh_object(name, verts, faces):
    """Creates a new mesh and object in the Blender scene."""
    me = bpy.data.meshes.new(name + "_mesh")
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    return obj

def final_mesh_cleanup(obj):
    """Performs final operations like removing doubles, subdividing, and smoothing."""
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=cfg.MERGE_DIST)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    
    for f in me.polygons:
        f.use_smooth = True
        
    if cfg.SUBDIVIDE_SMOOTH:
        subs = obj.modifiers.new("Subsurf", type='SUBSURF')
        subs.levels = cfg.SUBDIV_LEVELS
        subs.render_levels = max(1, cfg.SUBDIV_LEVELS)
        
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
    obj.location.z = 0.0