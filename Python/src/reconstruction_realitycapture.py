import subprocess
import os

def reconstruct():

    # Get the folder where this Python script is located
    root_folder = os.path.dirname(os.path.abspath(__file__))

    # Path to RealityCapture executable
    reality_capture_exe = r"C:\Program Files\Capturing Reality\RealityCapture\RealityCapture.exe"

    # Set working paths
    images_folder = os.path.join(root_folder, "imgs")
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

    # Run RealityCapture
    subprocess.run(command, shell=False)
