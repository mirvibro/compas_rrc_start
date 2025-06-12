"""
test script for sequencing function etc.
"""
import compas
from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z, target_frames_from_idx
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible, disassembly_workflow, print_penalty_forces
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.geometry import centroid_points
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.data import json_dump

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\finalwf_moved.json"


assembly = scan_to_CRA_assembly(mesh_file_path)
#assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=1e-1)
assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=5.1)
og_assembly = assembly.copy()

#connectivity_graph(assembly=assembly, vis=True)
goal_block = 13
""" 
assembly.delete_block(1)
assembly.delete_block(2)
assembly.delete_block(4)
cra_penalty_solve(assembly, density=1e-4, eps=1e-3, verbose=False, d_bnd=1e-3, mu=0.9)
 """
tf = disassembly_workflow(assembly=assembly, goal_block=goal_block, prints=True)

print_penalty_forces(assembly)
cra_view(assembly, nodal=False, scale=1, weights=False, forcesline=True, displacements=True)



#frames = target_frames_from_idx(assembly=og_assembly, idx=tf)

#connectivity_graph(assembly, vis=True, tags=True, vis_blocks=True)

def convert_frames_to_targetplanes(frames):
    planes = []
    for frame in frames: # [::-1]:
        plane_data = {
            "point": [frame.point[0] + 22.0, frame.point[1], frame.point[2] - 8.0],
            "x-axis": list(frame.xaxis),
            "y-axis": list(frame.yaxis)
        }
        planes.append(plane_data)
    
    # Wrap in final format
    formatted_data = {
        "TargetPlanes": {
            "Planes": planes
        }
    }

    return formatted_data

#json_dump(convert_frames_to_targetplanes(frames), "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\testframes_xz_adj_reassembly.json")

#target_frames_from_idx(assembly=og_assembly, idx=tf, vis=True, tags=True)

#get_forcesdirect(assembly=assembly)

""" m_viewer = Viewer(show_grid=False, width=1920, height=1080)
pi = []
for block in assembly.blocks():
    node_text = assembly.block_node(block)
    pi.append(block.center())
    tag = Tag(text=str(node_text), position=block.center())
    m_viewer.scene.add(tag)
    try:
        if node_text == goal_block:
            m_viewer.scene.add(block, show_faces=True, color=Color(0, 0.1, 0.9), opacity=0.5)
        elif node_text == 0:
            m_viewer.scene.add(block, show_faces=True, color=Color(0.8, 0.9, 0.8), opacity=1.0)        
        else:
            m_viewer.scene.add(block, show_faces=True, color=Color(0.9, 0.9, 0.9), opacity=0.5)
    except:
        if node_text == 0:
            m_viewer.scene.add(block, show_faces=True, color=Color(0.8, 0.9, 0.8), opacity=1.0)
        else:
            m_viewer.scene.add(block, show_faces=True, color=Color(0.9, 0.9, 0.9), opacity=0.5)
m_viewer.renderer.camera.target = centroid_points(pi)
m_viewer.show() """

""" for object in m_viewer.scene.objects:
    if object.is_selected == True:
        selected_block = object.mesh
        print(selected_block)
        print(selected_block.centroid) """

""" m_viewer.scene.clear()
m_viewer.renderer.clear() """

""" disassembly = assembly.copy()
blockers = z_blockers(assembly, goal_block)
for i in assembly.nodes():
    if i not in blockers and i != goal_block:
        #print(i)
        disassembly.delete_block(i)

remove = z_blockers(assembly, goal_block)
blocks_list = list(assembly.blocks())

remove_sorted = idx_presort_z(assembly, remove)
remove_sorted.append(goal_block)

print(remove_sorted) """

""" target_frames = target_frames_by_z(disassembly, vis=False)
viewer = Viewer()
#viewer.scene.add()
for order_nr, frame in enumerate(target_frames, start=1):
    tag = Tag(text=str(order_nr), position=frame.point)
    viewer.scene.add(tag)
for i in assembly.nodes():
    if i not in remove and i != goal_block:
        viewer.scene.add(assembly.node_block(i), show_faces=True)
    elif i == goal_block:
        viewer.scene.add(assembly.node_block(i), show_faces=True, color=Color(0, 0.1, 0.9), opacity=0.5)
    elif i in remove:
        viewer.scene.add(assembly.node_block(i), show_faces=False)
pi = []
for f in target_frames:
    pi.append(f.point)
viewer.renderer.camera.target = centroid_points(pi)  
viewer.show() """


""" 
mu = 0.9
dispbnd = 1e-2 #1e-1
overlap = 1e-4 #1e-3
d = 1e-5

og_assembly = assembly.copy()

for ridx, i in enumerate(remove_sorted, start=1):
    print(ridx, i)
final_disassembly_sequence = []
disassembly_printout = []
for ridx, i in enumerate(remove_sorted, start=1):
    block = blocks_list[i]
    assembly.delete_block(i)
    print(f"Evaluating removal of block #{ridx} with index {i}")
    if is_feasible(assembly, solver="CRA", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
        print(f"Removal of block #{ridx} with index {i} is structurally feasible")
        final_disassembly_sequence.append(i)
        disassembly_printout.append(f"Removal of block #{ridx} with index {i} is structurally feasible")
    else:
        print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible !!! trying cra_penalty_solve")
        if is_feasible(assembly, solver="CRA_penalty", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
            print(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")
            final_disassembly_sequence.append(i)
            disassembly_printout.append(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")
        else:
            print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible even with two-agent approach")


#cra_solve(assembly, verbose=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
#cra_penalty_solve(assembly, verbose=False, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
#cra_view(assembly)
print(assembly)
print(f"Final disassembly sequence: {final_disassembly_sequence}")
 """


""" for check in assembly.graph.nodes():
    print(assembly.graph.node_attribute(check, "displacement"))

for edge in assembly.graph.edges():
    interface = assembly.graph.edge_attribute(edge, "interfaces")[0]
    print(interface)
    forces = interface.forces
    print(forces)
    #print(assembly.graph.edge_attributes(edge)) """


#len(final_disassembly_sequence)

""" count_dis = len(frames)


save = []
save.append(count_dis)
assembly.delete_block(0)
for i in assembly.blocks():
    v, f = i.to_vertices_and_faces()
    save.append(Mesh.from_vertices_and_faces(v, f))
json_dump(save, "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\prefinal.json") """