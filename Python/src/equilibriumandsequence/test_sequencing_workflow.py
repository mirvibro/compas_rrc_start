"""
test script for sequencing function etc.
"""
import compas
from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.geometry import centroid_points
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.data import json_dump

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\wallsmall_not_overlapping.json" # change accordingly

mu = 0.9
dispbnd = 1e-1
overlap = 1e-3
d = 1

#cra_solve(assembly)
# cra_solve(assembly, verbose=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
#cra_penalty_solve(assembly, verbose=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
#rbe_solve(assembly)

assembly = scan_to_CRA_assembly(mesh_file_path)

assembly_interfaces_numpy(assembly, nmax=20, amin=1e-6, tmax=0.01)

goal_block = 17

#connectivity_graph(assembly, vis=True, tags=True, vis_blocks=True)
#assembly.delete_block(8)
#assembly.delete_block(21)


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
m_viewer.show()

for object in m_viewer.scene.objects:
    if object.is_selected == True:
        print(object)
        selected_block = object
        print(selected_block) """
    
#cra_penalty_solve(assembly, verbose=False, timer=True)
#cra_solve(assembly, mu=0.84, density=1.0, d_bnd=0.001, eps=0.001, verbose=False, timer=True)
#rbe_solve(assembly)

#cra_solve(assembly, verbose=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
#cra_penalty_solve(assembly, verbose=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)

#cra_view(assembly)
#cra_view_ex(m_viewer, assembly)
#viewer.show()



disassembly = assembly.copy()
blockers = z_blockers(assembly, goal_block)
for i in assembly.nodes():
    if i not in blockers and i != goal_block:
        #print(i)
        disassembly.delete_block(i)




#target_frames_by_z(disassembly, vis=True, tags=True)
target_frames = target_frames_by_z(disassembly, vis=False)

remove = z_blockers(assembly, goal_block)
print(remove)
blocks_list = list(assembly.blocks())

remove_sorted = idx_presort_z(assembly, remove)

""" viewer = Viewer()
#viewer.scene.add()
for order_nr, frame in enumerate(target_frames, start=1):
    tag = Tag(text=str(order_nr), position=frame.point)
    viewer.scene.add(tag)
for i in assembly.nodes():
    if i not in remove and i != goal_block:
        viewer.scene.add(assembly.node_block(i), show_faces=True)
    elif i == goal_block:
        viewer.scene.add(assembly.node_block(i), show_faces=True, color=Color(0, 0.1, 0.9))
    elif i in remove:
        viewer.scene.add(assembly.node_block(i), show_faces=False)
pi = []
for f in target_frames:
    pi.append(f.point)
viewer.renderer.camera.target = centroid_points(pi)  
viewer.show() """


""" savemeshes = []
for i in assembly.blocks():
    v, f = i.to_vertices_and_faces()
    savemeshes.append(Mesh.from_vertices_and_faces(v, f))
json_dump(savemeshes, "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\save2.json") """


final_disassembly_sequence = []
for ridx, i in enumerate(remove_sorted, start=1):
    block = blocks_list[i]
    assembly.delete_block(block)
    print(f"Evaluating removal of block #{ridx} with index {i}")
    if is_feasible(assembly, solver="CRA"):
        print(f"Removal of block #{ridx} with index {i} is structurally feasible")
        final_disassembly_sequence.append(i)
    elif not is_feasible(assembly, solver="CRA"):
        print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible !!! trying cra_penalty_solve")
        final_disassembly_sequence.append(i)
    elif is_feasible(assembly, solver="CRA_penalty"):
        print(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")
        final_disassembly_sequence.append(i)

print(final_disassembly_sequence)

