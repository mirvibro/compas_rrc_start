import subprocess
import os

def reconstruct():

    # Get the folder where this Python script is located
    root_folder = r"C:\Users\Miriam\compas_rrc_start"
    # Path to RealityCapture executable
    reality_capture_exe = r"C:\Program Files\Capturing Reality\RealityCapture\RealityCapture.exe"

    # Set working paths
    images_folder = os.path.join(root_folder, "imgs")
    print("Image folder contents:", os.listdir(images_folder))
    model_name = "Scan"
    model_output = os.path.join(root_folder, "Scan.obj")  # or change to .xyz, .las if point cloud
    project_output = os.path.join(root_folder, "Scan.rcproj")

    # Build RealityCapture CLI command
    command = [
        reality_capture_exe,
        "-addFolder", images_folder,
        "-align",
        "-setReconstructionRegionAuto",
        "-calculateNormalModel",            # Generates normal mesh (not textured)
        "-selectMarginalTriangles",
        "-removeSelectedTriangles",
        "-renameSelectedModel", model_name,
        # "-calculateTexture",              
        "-save", project_output,
        "-exportModel", model_name, model_output,
        "-quit"
    ]

    print("Running RealityCapture with command:")
    print(" ".join(command))

    # Run RealityCapture
    result = subprocess.run(command, capture_output=True, text=True)

    print("STDOUT:\n", result.stdout)
    print("STDERR:\n", result.stderr)

    if result.returncode != 0:
        print(f"RealityCapture failed with return code: {result.returncode}")

reconstruct()