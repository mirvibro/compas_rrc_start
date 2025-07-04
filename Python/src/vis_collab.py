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
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas_viewer.config import Config, DisplayConfig, RendererConfig
from compas.geometry import centroid_points, Polygon, Polyline, Vector, Line, Frame, Point, Circle, Cylinder, Plane
import compas
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas_viewer.config import Config, DisplayConfig, RendererConfig
from compas.geometry import centroid_points, Polygon, Polyline, Vector, Line, Frame, Point, Circle, Cylinder, Plane
import numpy as np
from compas.scene import Scene
from compas_viewer import HERE
from compas_viewer.config import Config
from compas_viewer.events import EventManager
from compas_viewer.mouse import Mouse
from compas_viewer.renderer import Renderer
from compas_viewer.scene import ViewerScene
from compas_viewer.singleton import Singleton
from compas_viewer.ui import UI
from compas_viewer import *

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

T1_assembly.delete_block(1)
T2_assembly.delete_block(1)

for block in list(T1_assembly.blocks()):
    node = T1_assembly.block_node(block)
    if node not in seq:
        T1_assembly.delete_block(node)
    else:
        block.transform(T)

for block in list(T2_assembly.blocks()):
    node = T2_assembly.block_node(block)
    if node not in seq:
        T2_assembly.delete_block(node)
    else:
        block.transform(T)


blocks_to_transform = [block
                       for block in T2_assembly.blocks()
                       if T2_assembly.block_node(block) in seq]

for block, transform in zip(blocks_to_transform, T_individual):
    block.transform(transform)


def my_viewer(og_assembly, T1_assembly, T2_assembly):

    def thick_line(line: Line, radius: float = 1.0) -> Mesh:
        cylinder = Cylinder.from_line_and_radius(line, radius)
        return cylinder.to_mesh()


    og_color= Color.from_hex("#7E7E7E")
    initial_color= Color.from_hex("#0011FF")
    indivdual_color= Color.from_hex("#00AA03")

    config_myviewer = Config(unit="mm")
    
    viewer = Viewer(width=1920, height=1080, config=config_myviewer)
    viewer.config.renderer.show_grid=False

    thick_lines1 = []

    for block in og_assembly.blocks():
        node_text = og_assembly.block_node(block)
        if node_text in seq:
            for edge in block.edges():
                line = block.edge_line(edge)
                thick_lines1.append(thick_line(line, 0.5))
        elif node_text == 0:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=Color.from_hex("#C7C7C7"), opacity=1.0)
        else:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=og_color, color=og_color, opacity=0.5)



    thick_lines=[]
    for block in T1_assembly.blocks():
        for edge in block.edges():
            line = block.edge_line(edge)
            thick_lines.append(thick_line(line, 0.6))

    thick_lines2=[]
    for block in T2_assembly.blocks():
        for edge in block.edges():
            line = block.edge_line(edge)
            thick_lines2.append(thick_line(line, 0.5))

    viewer.scene.add(thick_lines1, linecolor=og_color)
    viewer.scene.add(thick_lines, linecolor=initial_color)
    viewer.scene.add(thick_lines2, linecolor=indivdual_color)



    for block in T1_assembly.blocks():
        viewer.scene.add(block, show_faces=False, show_lines=True, linewidth=10, linecolor=initial_color, color=initial_color, opacity=0.3)

    for block in T2_assembly.blocks():
        viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=indivdual_color, color=indivdual_color, opacity=0.3)

    viewer.renderer.camera.target = [510, 450, 65]
    viewer.renderer.camera.position = [880, 130, 280]
    viewer.show()

my_viewer(og_assembly, T1_assembly, T2_assembly)