from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z
from compas_cra.algorithms import assembly_interfaces_numpy

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\free.json" # change accordingly

assembly = scan_to_CRA_assembly(mesh_file_path)

assembly_interfaces_numpy(assembly, nmax=7, amin=1e-4, tmax=1e-6)

#connectivity_graph(assembly, vis=True, vis_blocks=True)

target_frames_by_z(assembly, vis=True)