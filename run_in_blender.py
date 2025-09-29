import bpy
import sys
import os
import importlib

# --- Robust Path and Module Reloading ---
def get_script_dir():
    """Tries to get the directory of the currently running script."""
    # Check if the script is saved and has a real path
    if bpy.context.space_data.text.filepath:
        return os.path.dirname(bpy.context.space_data.text.filepath)
    return None

def add_project_to_path(package_name="mine_generator"):
    """
    Finds the project root (where the package and script live) and adds it
    to Python's path if it's not already there.
    """
    script_dir = get_script_dir()
    if not script_dir:
        # Raise an error to the user in Blender's UI
        raise Exception("Please save the script to a file before running!")

    # The project_dir is where 'run_in_blender.py' and 'mine_generator/' are
    project_dir = os.path.abspath(script_dir)
    
    # Check if the package actually exists in that directory
    package_path = os.path.join(project_dir, package_name)
    if not os.path.isdir(package_path):
        raise FileNotFoundError(f"Cannot find the '{package_name}' folder in '{project_dir}'. Please check your file structure.")

    # Add the project directory to Python's search path
    if project_dir not in sys.path:
        sys.path.append(project_dir)
    
    # For development: reload the package and its modules
    if package_name in sys.modules:
        package_module = sys.modules[package_name]
        for module_name in list(sys.modules.keys()):
            if module_name.startswith(package_name + '.'):
                importlib.reload(sys.modules[module_name])
        importlib.reload(package_module)

# --- Run the setup ---
try:
    add_project_to_path()
except (Exception, FileNotFoundError) as e:
    # Use Blender's UI to show the error message clearly
    bpy.ops.wm.call_popup(message=str(e))
    # Add a dummy main function to prevent further errors
    def main():
        print("Script execution stopped due to path error.")
else:
    # --- Import Generator Modules (now that the path is set) ---
    from mine_generator import config as cfg
    from mine_generator import utils
    from mine_generator import pit_generator
    from mine_generator import dump_generator
    from mine_generator import mesh_builder


def generate_terrain_data():
    """
    Orchestrates the data generation process by combining pit and dump calculations.
    Returns the final vertex and face data for mesh creation.
    """
    verts, faces = mesh_builder.make_grid()
    z_grid = [0.0] * len(verts)

    print("Calculating terrain elevations...")
    for i, v in enumerate(verts):
        x, y = v[0], v[1]
        
        # 1. Calculate the base pit depth (negative value)
        pit_z = pit_generator.compute_pit_depth(x, y)
        
        # 2. Calculate the overburden dump height (positive value)
        dump_h = dump_generator.compute_dump_height_at(x, y)
        
        # 3. Combine them
        if dump_h is None:
            final_z = pit_z
        else:
            # Create a gentle base terrain for dumps to sit on
            base_surface = utils.fbm(x * 0.0038, y * 0.0038, cfg.NOISE_SEED + 21, octaves=4) * 1.6 * cfg.VERTICAL_SCALE
            dump_world_z = base_surface + dump_h
            # The final surface is the higher of the pit or the dump
            final_z = max(pit_z, dump_world_z)
            
        z_grid[i] = final_z

    print("Applying erosion...")
    z_grid = mesh_builder.apply_erosion(z_grid)

    print("Blending outer edges...")
    for i, v in enumerate(verts):
        x, y = v[0], v[1]
        r, theta = math.hypot(x, y), math.atan2(y, x)
        eff_r = pit_generator.compute_effective_radius(theta)
        
        if r > eff_r * 0.98:
            surf = utils.fbm(x * 0.0035, y * 0.0035, cfg.NOISE_SEED + 21, octaves=4) * 1.6
            blend_t = utils.smoothstep((r - eff_r * 0.98) / max(1.0, cfg.SIZE * 0.08))
            z_grid[i] = utils.lerp(z_grid[i], surf * cfg.VERTICAL_SCALE, blend_t)

    # Apply the final Z-heights to the vertex list
    for i, v in enumerate(verts):
        v[2] = z_grid[i]
        
    return verts, faces


def main():
    """Main function to run the entire generation process."""
    print("="*50)
    print("STARTING PROCEDURAL MINE GENERATION")
    print(f"Seed: {cfg.NOISE_SEED}")
    print(f"Pit Centers: {pit_generator.PIT_CENTERS}")
    print(f"Working Face Angle (radians): {cfg.WORKING_FACE_ANGLE:.2f}")
    
    mesh_builder.clear_scene()
    
    verts, faces = generate_terrain_data()
    
    print("Building Blender mesh object...")
    obj = mesh_builder.build_mesh_object("OpenPit_WithDumps", verts, faces)
    
    if cfg.APPLY_VERTEX_COLORS:
        print("Applying vertex colors...")
        mesh_builder.add_vertex_colors(obj)
        
    print("Finalizing mesh...")
    mesh_builder.final_mesh_cleanup(obj)
    
    print("="*50)
    print("GENERATION COMPLETE!")
    print(f"Created: {obj.name}")
    print("="*50)


if __name__ == "__main__":
    import math # Add math import for use in this script
    main()