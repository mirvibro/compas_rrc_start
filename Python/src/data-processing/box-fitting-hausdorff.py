import trimesh
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R

def create_box_from_params(params):
    center = params[:3]
    angles = params[3:6]  # Euler angles
    extents = params[6:9]

    rot = R.from_euler('xyz', angles).as_matrix()
    transform = np.eye(4)
    transform[:3, :3] = rot
    transform[:3, 3] = center

    box = trimesh.creation.box(extents=extents)
    box.apply_transform(transform)
    return box

def hausdorff_distance(params, mesh_points, mesh):
    box = create_box_from_params(params)
    box_points = box.sample(1000)

    dist_mesh_to_box = trimesh.proximity.ProximityQuery(box).signed_distance(mesh_points)
    dist_box_to_mesh = trimesh.proximity.ProximityQuery(mesh).signed_distance(box_points)

    return max(np.abs(dist_mesh_to_box).max(), np.abs(dist_box_to_mesh).max())

def compute_best_box(mesh):
    mesh_points = mesh.sample(1000)

    T_init, extents_init = trimesh.bounds.oriented_bounds(mesh)
    center_init = np.linalg.inv(T_init)[:3, 3]
    angles_init = R.from_matrix(np.linalg.inv(T_init)[:3, :3]).as_euler('xyz')
    x0 = np.hstack((center_init, angles_init, extents_init))

    res = minimize(hausdorff_distance, x0, args=(mesh_points, mesh), method='Powell', options={'maxiter': 200})
    return create_box_from_params(res.x)

def compute_a_box(mesh):
    T, extents = trimesh.bounds.oriented_bounds(mesh)
    box = trimesh.creation.box(extents=extents)
    box.apply_transform(T)
    return box

def bound_the_boxes(input_path, output_path):
    mesh = trimesh.load(input_path)

    # Ensure it's a Trimesh, not a Scene
    if isinstance(mesh, trimesh.Scene):
        raise TypeError("Expected a single mesh, but got a scene. Use force='mesh' if needed.")

    # Split the mesh into connected components
    components = mesh.split(only_watertight=False)  # Returns a list of Trimesh objects

    print(f"Split into {len(components)} components.")

    # Combine them into a Scene with separate named geometries
    scene = trimesh.Scene()
    for i, part in enumerate(components):
        scene.add_geometry(part, node_name=f'part_{i}')
    
    bounding_boxes = []

    print("Starting computation")
    for mesh in components:
        box = compute_a_box(mesh)
        bounding_boxes.append(box)

    print("Starting concatenation")
    if bounding_boxes:
        combined = trimesh.util.concatenate(bounding_boxes)
        combined.export(output_path)
        print(f"Exported combined bounding boxes to {output_path}")
    else:
        print("No bounding boxes were created.")

# Example usage
bound_the_boxes("miscellaneous/SegmentedForProcessing.obj", "miscellaneous/-bounded.obj")