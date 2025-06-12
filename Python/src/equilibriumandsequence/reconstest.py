"""
test script for sequencing function etc.
"""
import compas
import os
import glob
from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible, resassembly_workflow, identify_failing_block, idx_presort_z_recon
from compas.datastructures import Graph, Mesh
from compas_assembly.datastructures import Block
from compas_cra.datastructures import CRA_Assembly
from compas.colors import Color
from compas_viewer import Viewer, viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.geometry import centroid_points, Box, bounding_box
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.viewers import cra_view, cra_view_ex
from compas.data import json_dump
from compas.files import OBJ
from natsort import natsorted
from my_viewer import my_viewer

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\finalwf_moved.json" # change accordingly

assembly = scan_to_CRA_assembly(mesh_file_path)

seq = [1, 2, 4, 18, 8, 7, 10, 11, 13]
for s in seq:
    assembly.delete_block(s)

old_nodes = []
for block in assembly.blocks():
    old_nodes.append(assembly.block_node(block))

output_folder = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\output_assemblies"
os.makedirs(output_folder, exist_ok=True)

mu = 0.9
dispbnd = 1e-3 #1e-1
overlap = 1e-3 #1e-3
d = 1e-4

folder = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\recons2"
pattern = os.path.join(folder, "Recon_IT-*.obj")
filepaths = natsorted(glob.glob(pattern))

feasibility_list = []
falling_blocks = []

assemblies = {}

""" for order, filepath in enumerate(filepaths):
    basename = os.path.splitext(os.path.basename(filepath))[0]
    name = f"assembly_{basename}"
    new_assembly = assembly.copy()
    new_assembly.name = name
    assemblies[name] = new_assembly

    obj = OBJ(filepath)
    obj.read()

    bbs = []
    for ob in obj.objects:
        mesh = Mesh.from_vertices_and_faces(*obj.objects[ob])
        mesh.weld()
        mp = mesh.vertices_attributes('xyz')
        bb = bounding_box(mp)
        bbs.append(bb)

    boxmeshes = []
    for b in bbs:
        box = Box.from_bounding_box(b)
        me = Mesh.from_shape(box)
        boxmeshes.append(me)

    sorted_boxmeshes = sorted(boxmeshes, key=lambda m: m.centroid()[2]) 

    for m in sorted_boxmeshes:
        new_assembly.add_block_from_mesh(m)

    assembly_interfaces_numpy(new_assembly, nmax=20, amin=1e-4, tmax=5.2)

    print(f"Evaluating assembly #{order}")

    try:
        cra_solve(new_assembly, verbose=False, density=d, d_bnd=dispbnd, eps=overlap, mu=mu)
        feasibility_list.append(True)
        falling_blocks.append([order, None])
    except Exception:
        feasibility_list.append(False)
        fb = identify_failing_block(new_assembly)[0]
        falling_blocks.append([order, fb])


    outpath = os.path.join(output_folder, f"{name}.json")
    new_assembly.to_json(outpath) """

#print(falling_blocks)

falling_blocks = [[26, 24, 25], [27], [25], [27, 26, 25, 24, 23, 22], [26], [24], [25], [21,22,25,26], [25,26], [27], [27, 26], [27], [], [], [], [], [27, 26], [27, 26, 25], [], [27, 26], [27], [], [27, 26, 25], [27], [27, 26]]

#a = assemblies["assembly_Recon_IT-83"]
#cra_view(a)
#print(feasibility_list)

feasibility_list = [False, False, True, False, False, False, False, True, True, False, False, False, True, True, True, True, False, False, True, False, False, True, False, False, False] 
#rf = resassembly_workflow(assembly, reassembly_file_path, prints=True)
#print(rf)

check_pattern = os.path.join(output_folder, "assembly_Recon_IT-*.json")
check_filepaths = natsorted(glob.glob(check_pattern))

""" for ord, file in enumerate(check_filepaths):
    if feasibility_list[ord] is True:
        check_assembly = CRA_Assembly.from_json(file)
        cra_view(check_assembly) """

checker = 1

check_assembly = CRA_Assembly.from_json(check_filepaths[checker])

new_nodes = []
for bl in check_assembly.blocks():
    if not check_assembly.block_node(bl) in old_nodes:
        new_nodes.append(check_assembly.block_node(bl))

""" fball = []
for blol in check_assembly.blocks():
    if not feasibility_list[checker] and check_assembly.block_node(blol) not in old_nodes:
        fball.append(check_assembly.block_node(blol)) """

sortidx = idx_presort_z_recon(check_assembly, new_nodes)
print(sortidx)

#sortidx = [19, 20, 21, 22, 23, 26, 24, 25, 27]
#sortidx = [19, 20, 21, 22, 24, 23, 26, 25, 27]
#sortidx = [19, 20, 21, 22, 24, 23, 25, 26, 27] #13
#sortidx = [19, 20, 21, 22, 25, 24, 23, 26, 27]

my_viewer(check_assembly, recontest=True, new_nodes=new_nodes, fb=falling_blocks[checker], dis_seq=sortidx)