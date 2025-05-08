from sequence import scan_to_CRA_assembly, target_frames_by_z
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.algorithms import assembly_interfaces_numpy
from compas_cra.viewers import cra_view, cra_view_ex
from compas_viewer import Viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.datastructures import Graph
from compas.colors import Color
from compas.geometry import centroid_points

def is_feasible(assembly, solver: str):
    if solver == "RBE":
        testsolver = rbe_solve
    elif solver == "CRA":
        solver == cra_solve
    elif solver == "CRA_penalty":
        solver == cra_penalty_solve
    else:
        raise ValueError(f"Unknown solver, available options are 'RBE' or 'CRA' or 'CRA_penalty'")
    try:
        testsolver(assembly)
        return True
    except Exception:
        return False

def z_blockers(assembly, testblock):

    graph = assembly.graph

    def direct_z_blockers(block):
        z_test = assembly.node_point(block).z
        return [
            nbr for nbr in graph.neighbors(block)
            if assembly.node_point(nbr).z > z_test
        ]

    def all_z_blockers(block, checked=None):
        if checked is None:
            checked = set()
        for nbr in direct_z_blockers(block):
            if nbr not in checked:
                checked.add(nbr)
                all_z_blockers(nbr, checked)
        return checked
    
    return all_z_blockers(testblock)

def idx_presort_z(assembly, to_remove):

    all_blocks = list(assembly.blocks())

    idx_and_frames = []
    for idx in to_remove:
        block = all_blocks[idx]
        top_face = block.top()
        frame = block.face_frame(top_face)
        frame.flip()
        idx_and_frames.append((idx, frame))

    idx_and_frames.sort(key=lambda pair: pair[1].point.z, reverse=True)

    sorted_indices = [idx for idx, _ in idx_and_frames]
    return sorted_indices
