import compas
from equilibriumandsequence.sequence import scan_to_CRA_assembly
from compas_cra.algorithms import assembly_interfaces_numpy
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas_viewer.config import Config
from compas.geometry import centroid_points, Polygon, Polyline, Vector, bounding_box, Box
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.files import OBJ

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\finalwf_moved.json"


assembly = scan_to_CRA_assembly(mesh_file_path)
assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=5.1)
og_assembly = assembly.copy()

seq = [1, 2, 4, 18, 8, 7, 10, 11, 13]

T_initial = compas.json_load("C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\json_leadThrough\\T_initial_1.json")
T = T_initial[0]
T_individual = compas.json_load("C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\json_leadThrough\\T_individual_1.json")

T1_assembly = assembly.copy()
T2_assembly = assembly.copy()

for block in T1_assembly.blocks():
    node_text = T1_assembly.block_node(block)
    if node_text not in seq:
        T1_assembly.delete_block(node_text)
        block.transformed(T)

for block in T2_assembly.blocks():
    node_text = T2_assembly.block_node(block)
    if node_text not in seq:
        T2_assembly.delete_block(node_text)


def my_viewer(og_assembly, T1_assembly, T2_assembly):


    og_color= Color.from_hex("#000000")
    initial_color= Color.from_hex("#000000")
    indivdual_color= Color.from_hex("#000000")

    config_myviewer = Config(unit="mm")
    
    viewer = Viewer(width=1920, height=1080, config=config_myviewer)
    viewer.config.renderer.show_grid=False

    for block in og_assembly.blocks():
        node_text = og_assembly.block_node(block)
        if node_text in seq:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=og_color, color=og_color, opacity=0.3)
        else:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=og_color, color=og_color, opacity=0.1)

    for block in T1_assembly.blocks():
        viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=initial_color, color=initial_color, opacity=0.3)

    for block in T2_assembly.blocks():
        viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=indivdual_color, color=indivdual_color, opacity=0.3)

    viewer.renderer.camera.target = [510, 450, 65]
    viewer.renderer.camera.position = [880, 130, 280]
    viewer.show()

my_viewer(og_assembly, T1_assembly, T2_assembly)