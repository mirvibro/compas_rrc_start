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
from compas.datastructures import Graph
from compas.geometry import Line
from compas.geometry import Frame
from compas_assembly.datastructures import Interface


#----------------------- robodesk: --------------------------#

d_x = 1350 #dimensions of desk
d_y = 1350

support = Box.from_corner_corner_height([0.0, 0.0, -10.0], [d_y, d_x, -10.0], 10.0)
#support = compas.json_load("C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\support.json") #old



#----------------------- load blocks: --------------------------#

free = compas.json_load("C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\free.json") #change filepath accordingly

assembly = CRA_Assembly()

assembly.add_block(Block.from_shape(support), node=0)

x=1 #replace with enumerate 
for i in free:
    assembly.add_block_from_mesh(i, node=x) 
    x+=1

#assembly.delete_block(1)
#assembly.delete_block(2)
#assembly.delete_block(3)



#----------------------- comput interfaces & set boundary conditions: --------------------------#

assembly_interfaces_numpy(assembly, nmax=7, amin=1e-4, tmax=1e-6)

assembly.set_boundary_conditions([0])

#assembly.unset_boundary_conditions()
#nodes = sorted(assembly.nodes(), key=lambda node: assembly.node_point(node).z)
#for node in nodes:
#    assembly.set_boundary_condition(node)



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



#----------------------- connectivity graph etc: --------------------------#

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



#----------------------- target planes: --------------------------#

top_face_planes = []
for block in assembly.blocks():
    topface = block.top()
    frame_og = block.face_frame(topface)
    frame_og.flip()
    top_face_planes.append(frame_og)
    print(frame_og)




#----------------------- solver & visualization: --------------------------#

#view without solver:

viewer = Viewer()
viewer.scene.add(free, show_faces=False)
viewer.scene.add(top_face_planes, framesize = [100, 100, 100, 100])
viewer.renderer.camera.target = [100, 100, 0]
viewer.renderer.camera.position = [500, -500, 200]
viewer.show()


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


