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
from compas_viewer.config import Config
from compas.geometry import centroid_points, Polygon, Polyline, Vector, bounding_box, Box
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.data import json_dump
from my_viewer import my_viewer
from compas.files import OBJ

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\finalwf_moved.json"


assembly = scan_to_CRA_assembly(mesh_file_path)
#assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=1e-1)
assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=5.1)
og_assembly = assembly.copy()

#connectivity_graph(assembly=assembly, vis=True)
goal_block = 13

pseq = [1, 2, 4, 7, 8, 18, 10, 11, 13]
seq = [1, 2, 4, 18, 8, 7, 10, 11, 13]
fb = 18

#frames = target_frames_from_idx(assembly=og_assembly, idx=tf)
old_nodes = []
for block in assembly.blocks():
    old_nodes.append(assembly.block_node(block))


""" 
for i in seq:
    assembly.delete_block(i)

reassembly_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\final-recon_1-exported.obj" 
obj = OBJ(reassembly_file_path)
obj.read()

bbs = []
for name in obj.objects:
    mesh = Mesh.from_vertices_and_faces(*obj.objects[name])
    mesh.weld()
    mp = mesh.vertices_attributes('xyz')
    bb = bounding_box(mp)
    bbs.append(bb)

for b in bbs:
    box = Box.from_bounding_box(b)
    me = Mesh.from_shape(box)
    assembly.add_block_from_mesh(me)
 """


new_nodes = []
for block in assembly.blocks():
    if assembly.block_node(block) not in old_nodes:
        new_nodes.append(assembly.block_node(block)) 


#rf = [19, 20, 21, 22, 26, 25, 23, 24, 27] #2
#fbr=[]
rf = [19, 27, 21, 26, 24, 22, 25, 20, 23] 
fbr = [22, 20]

#my_viewer(assembly, goal_block, conn_graph=True, tags=True, dis_seq=seq, fb=fb, justmesh=True, new_nodes=new_nodes)
#my_viewer(assembly, goal_block, interfaces=True, conn_graph=True, tags=True, dis_seq=seq, fb=fb, new_nodes=new_nodes)
my_viewer(assembly, goal_block, goal_block_vis=True, conn_graph_g=True, tags=True, dis_seq=seq, fb=fb, new_nodes=new_nodes)
#my_viewer(assembly, goal_block, dis=True, dis_seq=seq, fb=fb, new_nodes=new_nodes)
#my_viewer(assembly, goal_block, dis_seq=seq, fb=fbr, new_nodes=rf, new_nodes_vis=True)

#my_viewer(assembly, recontest=True, new_nodes=new_nodes, fb=[])