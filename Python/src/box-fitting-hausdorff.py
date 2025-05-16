import trimesh
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R

# Load the original mesh
mesh = trimesh.load("miscellaneous/scanned-block.obj")

# Compute the oriented bounding box (OBB)
#T, extents = trimesh.bounds.oriented_bounds(mesh)

# Create the oriented bounding box mesh
#obb = trimesh.creation.box(extents=extents, transform=np.linalg.inv(T))

# Export the OBB to an OBJ file
#obb.export("miscellaneous/scanned-block-obb.obj")

# Combine both meshes
#combined = trimesh.util.concatenate([mesh, obb])

# Export the combined mesh to a new OBJ file
#combined.export("miscellaneous/scanned-block-with-obb.obj")


# Sample points on the mesh
mesh_points = mesh.sample(1000)

def create_box_from_params(params):
    center = params[:3]
    angles = params[3:6]  # Euler angles
    extents = params[6:9]

    # Build transform: rotation + translation
    rot = R.from_euler('xyz', angles).as_matrix()
    transform = np.eye(4)
    transform[:3, :3] = rot
    transform[:3, 3] = center

    box = trimesh.creation.box(extents=extents)
    box.apply_transform(transform)
    return box

def hausdorff_distance(params):
    box = create_box_from_params(params)
    box_points = box.sample(1000)

    # One-sided Hausdorff distance: mesh -> box
    dist_mesh_to_box = trimesh.proximity.ProximityQuery(box).signed_distance(mesh_points)
    dist_box_to_mesh = trimesh.proximity.ProximityQuery(mesh).signed_distance(box_points)

    # Symmetric Hausdorff
    return max(np.abs(dist_mesh_to_box).max(), np.abs(dist_box_to_mesh).max())

# Initial guess: center, angles (rad), extents
T_init, extents_init = trimesh.bounds.oriented_bounds(mesh)
center_init = np.linalg.inv(T_init)[:3, 3]
angles_init = R.from_matrix(np.linalg.inv(T_init)[:3, :3]).as_euler('xyz')
x0 = np.hstack((center_init, angles_init, extents_init))

# Optimize
res = minimize(hausdorff_distance, x0, method='Powell', options={'maxiter': 200})

# Get final box
best_box = create_box_from_params(res.x)
combined = trimesh.util.concatenate([mesh, best_box])
combined.export("miscellaneous/scanned-block-with-tight-obb.obj")