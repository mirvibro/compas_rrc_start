"""
test script for sequencing function etc.
"""
import compas
from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z, target_frames_from_idx
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible, disassembly_workflow
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

class Arrow:
    def __init__(self, position=[0, 0, 0], direction=[0, 0, 1], linewidth=0.02):
        super().__init__()
        self.position = Vector(*position)
        self.direction = Vector(*direction)
        self.linewidth = linewidth

    def add_to_scene(self, viewer, facecolor: Color, opacity=1):
        viewer.scene.add(
            Vector(*self.direction),
            anchor=Point(*self.position),
            facecolor=facecolor,
            linecolor=facecolor,
            linewidth=self.linewidth,
            show_lines=True,
            opacity=opacity,
        )

def draw_interfaces(assembly, viewer):
    interfaces = []
    faces = []
    for edge in assembly.graph.edges():
        interface = assembly.graph.edge_attribute(edge, "interface")
        if interface is not None:
            corners = np.array(interface.points)
            faces.append(Polyline(np.vstack((corners, corners[0]))))
            if assembly.graph.node_attribute(edge[0], "is_support") or assembly.graph.node_attribute(
                edge[1], "is_support"
            ):
                continue
            polygon = Polygon(interface.points)
            #interfaces.append(Mesh.from_polygons([polygon]))
        if assembly.graph.edge_attribute(edge, "interfaces") is None:
            continue
        for subinterface in assembly.graph.edge_attribute(edge, "interfaces"):
            altpoints = [point + [0, 0, 0.05] for point in subinterface.points]
            corners = np.array(altpoints)
            faces.append(Polyline(np.vstack((corners, corners[0]))))
            polygon = Polygon(altpoints)
            interfaces.append(Mesh.from_polygons([polygon]))



    if len(interfaces) != 0:
        viewer.scene.add(
            interfaces,
            show_lines=True,
            linecolor=Color.from_hex("#000DFF"),
            linewidth=100,
            show_points=False,
            facecolor=Color.from_hex("#6970F9"),
        )
    for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0)        
            else:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_light, opacity=0.1)
                #print(viewer.scene.objects[-1].linewidth)

def conn_graph_v(assembly, viewer):

    og_edges = []
    for edge in assembly.edges():
        e = assembly.edge_line(edge)
        og_edges.append(e)

    revised_edges = og_edges.copy()
    for index, edgetest in enumerate(revised_edges):
        if edgetest.start.z < 0:
            revised_edges[index] = Line([edgetest.end.x, edgetest.end.y, -10.0], edgetest.end) 
        elif edgetest.end.z < 0:
            revised_edges[index] = Line(edgetest.start, [edgetest.start.x, edgetest.start.y, -10.0]) 

    thick_lines=[]
    for e in revised_edges:
        thick_lines.append(thick_line(e, 0.15))

    viewer.scene.add(thick_lines, linecolor=Color.from_hex("#000000"))

def conn_graph_gv(assembly, dis_seq, goal_block, viewer):

    og_edges = []
    for edge in assembly.edges():
        if edge[0] in dis_seq and edge[1] in dis_seq:
            e = assembly.edge_line(edge)
            og_edges.append(e)

    revised_edges = og_edges.copy()
    for index, edgetest in enumerate(revised_edges):
        if edgetest.start.z < 0:
            revised_edges[index] = Line([edgetest.end.x, edgetest.end.y, -10.0], edgetest.end) 
        elif edgetest.end.z < 0:
            revised_edges[index] = Line(edgetest.start, [edgetest.start.x, edgetest.start.y, -10.0])
        edgetest.start.x += -6
        edgetest.end.x += -6
        edgetest.start.y += 4
        edgetest.end.y += 4
        edgetest.start.z += -3
        edgetest.end.z += -3

    thick_lines=[]
    for e in revised_edges:
        thick_lines.append(thick_line(e, 1))

    graphlinecolour=Color.from_hex("#108A00")
    viewer.scene.add(thick_lines, color=graphlinecolour, linecolor=graphlinecolour)

    for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0) 
            elif node_text == goal_block:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_goalblock, opacity=0.5)            
            elif node_text in dis_seq:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_blocks_light, opacity=0.5)  
            else:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_dark, opacity=1.0)
        

def vis_tags(assembly, viewer):
    for block in assembly.blocks():
        node_text = assembly.block_node(block)
        point = block.center()
        tag = Tag(text=str(node_text), position=point, vertical_align="center", horizontal_align="center")
        #circle = Circle(radius=80, frame=Frame())
        #viewer.scene.add(point, pointsize=100, pointcolor=Color.from_hex("#FFFFFF"))
        viewer.scene.add(tag)
        
def dis_v(assembly, viewer, dis_seq, fb, goal_block):
    for d,i in enumerate(dis_seq, start=1):
        block = assembly.node_block(i)
        point = block.center()
        tag = Tag(text=str(d), position=point, vertical_align="center", horizontal_align="center")
        viewer.scene.add(tag)

    #dis_seq.remove(fb)
    for block in assembly.blocks():
        node_text = assembly.block_node(block)
        if node_text == 0:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0) 
        elif node_text == fb:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_falling, opacity=0.5)
        elif node_text == goal_block:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_goalblock, opacity=0.5)  
        elif node_text in dis_seq:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_ok, opacity=0.5)        
        else:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_dark, opacity=1.0)
    
    z=40
    testl = Arrow([559.92999293, 357.77358894, 63.01846695+15], [0, 0, z], 1)
    testl.add_to_scene(viewer, facecolor=c_falling)
    line = Line([559.92999293, 357.77358894, 63.01846695+15],[559.92999293, 357.77358894, 63.01846695+z+14])
    viewer.scene.add(thick_line(line, 0.3), linecolor=c_falling)

def recontestfalse(assembly, viewer, new_nodes, fb, dis_seq):

    for d,i in enumerate(dis_seq, start=1):
        block = assembly.node_block(i)
        point = block.center()
        tag = Tag(text=str(d), position=point, vertical_align="center", horizontal_align="center")
        viewer.scene.add(tag)

    for block in assembly.blocks():
        node_text = assembly.block_node(block)
        if node_text == 0:
            continue
            #viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0) 
        elif node_text in fb:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_falling, opacity=0.5)     
        elif node_text in new_nodes:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_ok, opacity=0.5)   
        else:
            viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_dark, opacity=1.0)
    z=45
    for k in fb:
        blo = assembly.node_block(k)
        poi = blo.center()
        arr = Arrow(poi, [0, 0, z], 1)
        arr.add_to_scene(viewer, facecolor=c_falling)
        viewer.scene.add(thick_line(Line.from_point_and_vector(poi, [0, 0, z-2]), 0.3), linecolor=c_falling)


def thick_line(line: Line, radius: float = 1.0) -> Mesh:
    cylinder = Cylinder.from_line_and_radius(line, radius)
    return cylinder.to_mesh()


c_desk = Color.from_hex("#AAAAAA")
c_blocks_dark = Color.from_hex("#797979")
c_blocks_light = Color.from_hex("#D1D1D1")
c_goalblock = Color.from_hex("#245EFF")
c_ok = Color.from_hex("#078909")
c_falling = Color.from_hex("#EB1212")

def my_viewer(
    assembly,
    goal_block=[],
    goal_block_vis=False,
    tags=False,
    dis=False,
    dis_seq=[],
    fb=[],
    new_nodes=[],
    new_nodes_vis=False,
    justmesh=False,
    scale=1.0,
    density=1.0,
    dispscale=1.0,
    tol=1e-5,
    grid=False,
    resultant=True,
    nodal=False,
    edge=True,
    blocks=True,
    interfaces=False,
    forces=True,
    forcesdirect=True,
    forcesline=False,
    weights=True,
    displacements=True,
    conn_graph=False,
    conn_graph_g=False,
    recontest=False
    ):

    config_myviewer = Config(unit="mm")
    
    viewer = Viewer(width=1920, height=1080, config=config_myviewer)
    viewer.config.renderer.show_grid=False


    """ if blocks:
        draw_blocks(assembly, viewer, edge, tol)
    if forces:
        draw_forces(assembly, viewer, scale, resultant, nodal)
    if forcesdirect:
        draw_forcesdirect(assembly, viewer, scale, resultant, nodal)
    if forcesline:
        draw_forcesline(assembly, viewer, scale, resultant, nodal)
    if weights:
        draw_weights(assembly, viewer, scale, density)
    if displacements:
        draw_displacements(assembly, viewer, dispscale, tol) """
    if recontest:
        recontestfalse(assembly, viewer, new_nodes, fb, dis_seq)
    if interfaces:
        draw_interfaces(assembly, viewer)
    if conn_graph:
        conn_graph_v(assembly, viewer)
    if conn_graph_g:
        conn_graph_gv(assembly, dis_seq, goal_block, viewer)
    if justmesh:
        for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0)        
            elif goal_block_vis:
                if node_text == goal_block:
                    viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_goalblock, opacity=0.5)
                else:
                    viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=float(50), linecolor=Color.from_hex("#000000"), color=c_blocks_light, opacity=0.5)
            else:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_dark, opacity=0.5)
                #print(viewer.scene.objects[-1].linewidth)
    if tags:
        vis_tags(assembly, viewer)
    if dis:
        dis_v(assembly, viewer, dis_seq, fb, goal_block)
    if new_nodes_vis:
        for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_desk, opacity=1.0)        
            elif node_text in fb:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_falling, opacity=0.5)
            elif node_text in new_nodes:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=20, linecolor=Color.from_hex("#000000"), color=c_ok, opacity=0.5)
            else:
                viewer.scene.add(block, show_faces=True, show_lines=True, linewidth=10, linecolor=Color.from_hex("#000000"), color=c_blocks_dark, opacity=1.0)
        
        for d,i in enumerate(new_nodes, start=1):
            block = assembly.node_block(i)
            point = block.center()
            tag = Tag(text=str(d), position=point, vertical_align="center", horizontal_align="center")
            viewer.scene.add(tag)

        z=55
        for k in fb:
            blo = assembly.node_block(k)
            poi = blo.center()
            arr = Arrow(poi, [0, 0, z], 1)
            arr.add_to_scene(viewer, facecolor=c_falling)
            viewer.scene.add(thick_line(Line.from_point_and_vector(poi, [0, 0, z-2]), 0.3), linecolor=c_falling)

                
    #[559.92999293 367.77358894  63.01846695] Vector(x=0.000, y=0.000, z=5.400)


    #viewer.renderer.camera.target = [520, 470, 70]
    #viewer.renderer.camera.position = [895, 145, 285]
    viewer.renderer.camera.target = [510, 450, 65]
    viewer.renderer.camera.position = [880, 130, 280]
    viewer.config.ui.display.linewidth = 100
    viewer.show()