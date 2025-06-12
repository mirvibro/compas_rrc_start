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
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.geometry import centroid_points
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.data import json_dump

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\wallsmall.json" # change accordingly


assembly = scan_to_CRA_assembly(mesh_file_path)

assembly_interfaces_numpy(assembly, nmax=20, amin=1e-6, tmax=0.001)

goal_block = 3

disassembly = assembly.copy()
blockers = z_blockers(assembly, goal_block)
for i in assembly.nodes():
    if i not in blockers:
        #print(i)
        disassembly.delete_block(i)

remove = z_blockers(assembly, goal_block)
blocks_list = list(assembly.blocks())

remove_sorted = idx_presort_z(assembly, remove)
remove_sorted.append(goal_block)

for r in remove_sorted:
    assembly.delete_block(r)


remove_sorted.reverse()


mu = 0.9
dispbnd = 1e-1
overlap = 1e-3
d = 1

for ridx, i in enumerate(remove_sorted, start=1):
    print(ridx, i)
final_resassembly_sequence = []
resassembly_printout = []
for ridx, i in enumerate(remove_sorted, start=1):
    block = blocks_list[i]
    assembly.add_block(i)
    print(f"Evaluating assembly of block #{ridx} with index {i}")
    if is_feasible(assembly, solver="CRA", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
        print(f"Assembly of block #{ridx} with index {i} is structurally feasible")
        final_resassembly_sequence.append(i)
        resassembly_printout.append(f"Removal of block #{ridx} with index {i} is structurally feasible")
    else:
        print(f"!!! Assembly of block #{ridx} with index {i} is structurally infeasible !!! trying cra_penalty_solve")
        if is_feasible(assembly, solver="CRA_penalty", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
            print(f"Assembly of block #{ridx} with index {i} is structurally feasible with additional forces x...")
            final_resassembly_sequence.append(i)
            resassembly_printout.append(f"Assembly of block #{ridx} with index {i} is structurally feasible with additional forces x...")
        else:
            print(f"!!! Assembly of block #{ridx} with index {i} is structurally infeasible even with two-agent approach")

cra_penalty_solve(assembly, verbose=False, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
cra_view(assembly)
print(assembly)
print(f"Final disassembly sequence: {final_resassembly_sequence}")
for printout in resassembly_printout:
    print(printout)

