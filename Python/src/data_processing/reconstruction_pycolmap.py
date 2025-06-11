import pycolmap
import os

output_path = "reconstruction"
image_dir = "imgs"

def reconstruct():

    # Create output directory if it doesn't exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # Prepare paths
    mvs_path = os.path.join(output_path, "mvs")
    database_path = os.path.join(output_path, "database.db")

    # Step 1: Feature Extraction
    pycolmap.extract_features(database_path, image_dir)

    # Step 2: Matching
    pycolmap.match_exhaustive(database_path)

    # Step 3: Sparse Reconstruction
    maps = pycolmap.incremental_mapping(database_path, image_dir, output_path)
    if not maps:
        raise RuntimeError("No reconstruction was created.")
    maps[0].write(output_path)
    
    # Step 4: Dense Reconstruction
    #pycolmap.undistort_images(mvs_path, output_path, image_dir)
    #pycolmap.patch_match_stereo(mvs_path)  # requires compilation with CUDA
    #pycolmap.stereo_fusion(mvs_path / "dense.ply", mvs_path)
