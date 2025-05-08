"""
test script for sequencing function etc.
"""

from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible
from compas.datastructures import Graph
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\wall3.json" # change accordingly

assembly = scan_to_CRA_assembly(mesh_file_path)

assembly_interfaces_numpy(assembly, nmax=20, tmax=1e-6)

goal_block = 7

#connectivity_graph(assembly, vis=True, tags=True, vis_blocks=True)

#print(z_blockers(assembly, goal_block))

#assembly.delete_block(8)

#for block in assembly.blocks():
#    print(assembly.block_node(block))

""" disassembly = assembly.copy()
blockers = z_blockers(assembly, goal_block)
for i in assembly.nodes():
    if i not in blockers and i != goal_block:
        print(i)
        disassembly.delete_block(i) """


#print(idx_presort_z(assembly, remove))


#connectivity_graph(assembly, vis=True, tags=True, vis_blocks=True)

#target_frames_by_z(disassembly, vis=True, tags=True)
#target_frames_by_z(disassembly, vis=True, tags=True)


remove = z_blockers(assembly, goal_block)

blocks_list = list(assembly.blocks())

for ridx, i in enumerate(remove, start=1):
    block = blocks_list[i]
    assembly.delete_block(block)
    print(f"Evaluating removal of block #{ridx} with index {i}")
    if is_feasible(assembly, solver="RBE"):
        print(f"Removal of block #{ridx} with index {i} is structurally feasible")
    elif not is_feasible(assembly, solver="RBE"):
        print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible !!! trying cra_penalty_solve")
    elif is_feasible(assembly, solver="CRA_penalty"):
        print(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")