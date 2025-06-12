""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!   WIP   !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """
""" !!!!!!!!!         !!!!!!!!! """

import os
import compas
import compas_cra
from compas.geometry import Box, Line, Frame, centroid_points
from compas.datastructures import Graph, Mesh
from compas_cra.datastructures import CRA_Assembly
from compas_cra.equilibrium import cra_solve, cra_penalty_solve
from compas_cra.algorithms import assembly_interfaces_numpy
from compas_cra.viewers import cra_view
from compas_assembly.datastructures import Block, Interface
from compas_viewer import Viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.colors import Color



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
    d_x = 1450 #dimensions of desk
    d_y = 1450

    support = Box.from_corner_corner_height([0.0, 0.0, -10.0], [d_y, d_x, -10.0], 10.0)

    free = compas.json_load(filepath)

    assembly = CRA_Assembly()

    assembly.add_block(Block.from_shape(support), node=0)

    for i,mesh in enumerate(free, start=1):
        assembly.add_block_from_mesh(mesh, node=i)

    assembly.set_boundary_conditions([0])

    print("Successfully converted meshes and set boundary conditions for assembly")

    return assembly



def connectivity_graph(assembly, vis=True, tags=True, vis_blocks=False):
    """
    constructs connectivity graph
    visualisation with compas_viewer

    Parameters:

        assembly: class: compas_cra.datastructures.CRA_Assembly
            the assembly to analize

        vis: bool, optional
            if True, visualization with compas_viewer

        tags: bool, optional
            if True, show node tags   

        vis_blocks: bool,optional
            if True, shows blocks as wireframe

    Returns:

        None

    """
    nodepoints = [] 
    for block in assembly.blocks():
        node = assembly.block_node(block)
        nodepoints.append(assembly.node_point(node))

    # edges as structured internally
    og_edges = []
    for edge in assembly.edges():
        print(edge)
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
        if tags == True:
            print("check")
            for block in assembly.blocks():
                node_text = assembly.block_node(block)
                n_point = assembly.node_point(node_text)
                tag = Tag(text=str(node_text), position=n_point) 
                viewer.scene.add(tag)        
        if vis_blocks == True:
            for block in assembly.blocks():
                viewer.scene.add(block, show_faces=False)
        viewer.renderer.camera.target = centroid_points(nodepoints)                
        viewer.show()
    else:
        print("Set vis=True to visualize")

    return None


def target_frames_by_z(assembly, save_frames=False, vis=False, tags=False):
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

        tags: bool, optional
            if True, show frame tags             

    Returns:

        target_frames: list[class: compas.geometry.Frame]
            list of sorted target frames

    """
    free_assembly = assembly.copy()
    free_assembly.delete_block(0)

    top_face_frames = []
    for block in free_assembly.blocks():
        topface = block.top()
        frame_og = block.face_frame(topface)
        frame_og.flip()
        top_face_frames.append(frame_og)

    #which axis is the gripper oriented towards?

    def frame_z(frame):
        return frame.point.z

    targetframes_sorted = sorted(top_face_frames,reverse=True, key=frame_z)

    if vis == True:
        viewer = Viewer()
        viewer.scene.add(targetframes_sorted)
        if tags == True:
            for order_nr, frame in enumerate(targetframes_sorted, start=1):
                tag = Tag(text=str(order_nr), position=frame.point)
                viewer.scene.add(tag)
        for block in assembly.blocks():
            viewer.scene.add(block, show_faces=False)
        frame_points = []
        for frame in targetframes_sorted:
            frame_points.append(frame.point)
        viewer.renderer.camera.target = centroid_points(frame_points)
        #viewer.renderer.camera.position = [500, -500, 200]
        viewer.show()
    else:
        print("Set vis=True to visualize frames")

    if save_frames == True: # to do
        print("Saving as file not implemented yet, please tell Michael he's lazy")

    return targetframes_sorted

def target_frames_from_idx(assembly, idx=[], save_frames=False, vis=False, tags=False):

    blocks_list = list(assembly.blocks())
    top_face_frames = []
    for i in idx:
        block = blocks_list[i]
        topface = block.top()
        frame_og = block.face_frame(topface)
        #frame_og.flip()
        top_face_frames.append(frame_og)

    l = len(idx)
    if l > 1:
        blue_shades = [(0, 0, 0.5 + (1 - 0.5) * i / (l - 1)) for i in range(l)]
    else:
        blue_shades = [(0, 0, 1.0)] 
    
    color_map = {val: blue_shades[i] for i, val in enumerate(idx)}

    if vis == True:
        viewer = Viewer()
        viewer.scene.add(top_face_frames)
        if tags == True:
            for order_nr, frame in enumerate(top_face_frames, start=1):
                tag = Tag(text=str(order_nr), position=frame.point)
                viewer.scene.add(tag)
        for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, color=Color(0.8, 0.9, 0.8), opacity=1.0)   
            elif node_text in color_map:
                r, g, b = 0.3, 0.3, color_map[node_text][2]
                viewer.scene.add(block, show_faces=True, color=Color(r, g, b), opacity=0.6)
            else:
                viewer.scene.add(block, show_faces=True, color=Color(0.9, 0.9, 0.9), opacity=1.0)
        frame_points = []
        for frame in top_face_frames:
            frame_points.append(frame.point)
        viewer.renderer.camera.target = centroid_points(frame_points)
        #viewer.renderer.camera.position = [500, -500, 200]
        viewer.show()
    else:
        print("Set vis=True to visualize frames")

    if save_frames == True: # to do
        print("Saving as file not implemented yet, please tell Michael he's lazy")

    return top_face_frames

def target_frames_from_idx_recon(assembly, idx=[], save_frames=False, vis=False, tags=False):


    top_face_frames = []
    for i in idx:
        block = assembly.node_block(i)
        topface = block.top()
        frame_og = block.face_frame(topface)
        #frame_og.flip()
        if frame_og.normal.z > 0:
            frame_og.flip()
        top_face_frames.append(frame_og)

    l = len(idx)
    if l > 1:
        blue_shades = [(0, 0, 0.5 + (1 - 0.5) * i / (l - 1)) for i in range(l)]
    else:
        blue_shades = [(0, 0, 1.0)] 
    
    color_map = {val: blue_shades[i] for i, val in enumerate(idx)}

    if vis == True:
        viewer = Viewer()
        viewer.scene.add(top_face_frames)
        if tags == True:
            for order_nr, frame in enumerate(top_face_frames, start=1):
                tag = Tag(text=str(order_nr), position=frame.point)
                viewer.scene.add(tag)
        for block in assembly.blocks():
            node_text = assembly.block_node(block)
            if node_text == 0:
                viewer.scene.add(block, show_faces=True, color=Color(0.8, 0.9, 0.8), opacity=1.0)   
            elif node_text in color_map:
                r, g, b = 0.3, 0.3, color_map[node_text][2]
                viewer.scene.add(block, show_faces=True, color=Color(r, g, b), opacity=0.6)
            else:
                viewer.scene.add(block, show_faces=True, color=Color(0.9, 0.9, 0.9), opacity=1.0)
        frame_points = []
        for frame in top_face_frames:
            frame_points.append(frame.point)
        viewer.renderer.camera.target = centroid_points(frame_points)
        #viewer.renderer.camera.position = [500, -500, 200]
        viewer.show()
    else:
        print("Set vis=True to visualize frames")

    if save_frames == True: # to do
        print("Saving as file not implemented yet, please tell Michael he's lazy")

    return top_face_frames