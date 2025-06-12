"""
test script for sequencing function etc.
"""
import compas
from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z, target_frames_from_idx, target_frames_from_idx_recon
from compas_cra.algorithms import assembly_interfaces_numpy
from partial_disassembly import z_blockers, idx_presort_z, is_feasible, resassembly_workflow
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

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\finalwf_moved.json" # change accordingly


assembly = scan_to_CRA_assembly(mesh_file_path)

seq = [1, 2, 4, 18, 8, 7, 10, 11, 13]
for i in seq:
    assembly.delete_block(i)


reassembly_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\final-recon_1-exported.obj" 

#rf = resassembly_workflow(assembly, reassembly_file_path, prints=True)
#print(rf)
#cra_view(assembly)


obj = OBJ(reassembly_file_path)
obj.read()

bbs = []
for name in obj.objects:
    mesh = Mesh.from_vertices_and_faces(*obj.objects[name])
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
    assembly.add_block_from_mesh(m)

rf = [19, 20, 21, 22, 24, 23, 25, 26, 27] # [19, 20, 21, 22, 26, 25, 23, 24, 27]

#rf = [19, 20, 21, 22, 24, 23, 26, 25, 27]

frames = target_frames_from_idx_recon(assembly=assembly, idx=rf, vis=True, tags=True)


def convert_frames_to_targetplanes(frames):
    planes = []
    for frame in frames: # [::-1]:
        plane_data = {
            "point": [frame.point[0] + 22.0, frame.point[1], frame.point[2] - 3.0],
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

#json_dump(convert_frames_to_targetplanes(frames), "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\recon2_2.json")