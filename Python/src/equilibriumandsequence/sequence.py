""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!   WIP   !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """

import os

import compas

import compas_cra
from compas.geometry import Box
from compas_cra.datastructures import CRA_Assembly
from compas.datastructures import Mesh
from compas_cra.equilibrium import cra_solve
from compas_cra.equilibrium import cra_penalty_solve
from compas_cra.algorithms import assembly_interfaces_numpy
from compas_assembly.datastructures import Block
from compas_cra.viewers import cra_view
from compas_viewer import Viewer
from compas_viewer.scene import Tag
from compas_viewer.scene import FrameObject
from compas.datastructures import Graph
from compas.geometry import Line
from compas.geometry import Frame
from compas_assembly.datastructures import Interface




def scan_to_CRA_assembly(filepath: str):
    """
    load the assembly from the scanning routine and convert into CRA_assembly 
    also includes the robodesk
    defines robodesk as support by setting boundary condition
    
    Parameters:

        filepath: str
            location of scan, currently needs to be .json file

    Returns:

        assembly:  class: compas_cra.datastructures.CRA_Assembly

    """
    d_x = 1350 #dimensions of desk
    d_y = 1350

    support = Box.from_corner_corner_height([0.0, 0.0, -10.0], [d_y, d_x, -10.0], 10.0)

    free = compas.json_load(filepath)

    assembly = CRA_Assembly()

    assembly.add_block(Block.from_shape(support), node=0)

    for i,mesh in enumerate(free, start=1):
        assembly.add_block_from_mesh(mesh, node=i)

    assembly.set_boundary_conditions([0])

    print("Successfully converted meshes and set boundary conditions for assembly")

    return assembly

#----------------------- comput interfaces & set boundary conditions: --------------------------#

assembly_interfaces_numpy(assembly, nmax=7, amin=1e-4, tmax=1e-6)






#----------------------- diagnostics: --------------------------#

""" 
for block in assembly.blocks():
    face_keys = list(block.faces())  
    for fkey in face_keys:
        print("Block node:", assembly.block_node(block), "face key:", fkey,"Face attributes:", block.face_attributes(fkey))#, "face vertices:", block.face_vertices(fkey), "face coordinates:", block.face_coordinates(fkey))
 """

if_list = []
for l in assembly.interfaces():
    if_list.append(l.polygon)



def connectivity_graph(assembly, vis=True, vis_blocks=False):
    """
    constructs connectivity graph
    visualisation with compas_viewer

    Parameters:

        assembly: class: compas_cra.datastructures.CRA_Assembly
            the assembly to analize

        vis: bool, optional
            if True, visualization with compas_viewer

        vis_blocks: bool,optional
            if True, shows blocks as wireframe

    Returns:

        None

    """
    nodepoints = [] 
    #node_tags = []
    for block in assembly.blocks():
        node = assembly.block_node(block)
        nodepoints.append(assembly.node_point(node))
        #node_tags.append(Tag(block_node(block)))

    # edges as structured internally
    og_edges = []
    for edge in assembly.edges():
        e = assembly.edge_line(edge)
        og_edges.append(e)

    # reconstruct edges connecting to support to just connect straight downwards onto the robodesk instead of to the node in its center
    revised_edges = og_edges.copy()
    for index, edgetest in enumerate(revised_edges):
        if edgetest.start.z < 0:
            revised_edges[index] = Line([edgetest.end.x, edgetest.end.y, -10.0], edgetest.end) 
        elif edgetest.end.z < 0:
            revised_edges[index] = Line(edgetest.start, [edgetest.start.x, edgetest.start.y, -10.0]) 

    if vis == True:
        viewer = Viewer()
        viewer.scene.add(revised_edges)
        if vis_blocks == True:
            for block in assembly.blocks():
                viewer.scene.add(block, show_faces=False)
        viewer.show()
    else:
        print("Set vis=True to visualize")

    return None


def target_frames_by_z(assembly, save_frames=False, vis=False):
    """
    computes frames for robot targets from the assembly by sorting by z height
    option to save them locally
    option to visualize disassembly sequence

    Parameters:

        assembly: class: compas_cra.datastructures.CRA_Assembly
            the assembly to compute the disassembly sequence from

        save_frames: bool, optional
            if True, saves the frames locally

        vis: bool, optional
            if True, visualizes the disassembly sequence

    Returns:

        target_frames: list[class: compas.geometry.Frame]
            list of sorted target frames

    """
    top_face_frames = []
    for block in assembly.blocks():
        topface = block.top()
        frame_og = block.face_frame(topface)
        frame_og.flip()
        top_face_frames.append(frame_og)

    #print(top_face_frames)

    #which axis is the gripper oriented towards?

    targetframes_sorted = []
    frame_point_zheights = []
    for block in assembly.blocks():
        topface = block.top()
        frame_og = block.face_frame(topface)
        frame_og.flip()
        frame_point_zheights.append(frame_og.point.z)

    print(frame_point_zheights)

    return target_frames



#----------------------- solver & visualization: --------------------------#

#view without solver:

viewer = Viewer()
viewer.scene.add(top_face_frames)
#viewer.scene.scale(100)
#viewer.scene.add(FrameObject(top_face_frames, [100, 100, 100, 100], show_framez = True))
#viewer.add(FrameObject(top_face_frames, [100, 100, 100, 100], show_framez = True))
viewer.scene.add(free, show_faces=False)
viewer.renderer.camera.target = [100, 100, 0]
viewer.renderer.camera.position = [500, -500, 200]
#viewer.show()


""" cra_penalty_solve(assembly, verbose=True, timer=True, density=0.1)
#cra_view(assembly)
cra_view(
    assembly,
    scale=0.001,
    density=1.0,
    dispscale=1.0,
    grid=False,
    resultant=True,
    nodal=True,
    edge=True,
    blocks=True,
    interfaces=True,
    forces=True,
    forcesdirect=True,
    forcesline=True,
    weights=True,
    displacements=True,
) """

#----------------------- solver loop: --------------------------#


