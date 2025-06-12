from sequence import scan_to_CRA_assembly, connectivity_graph, target_frames_by_z, target_frames_from_idx
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.algorithms import assembly_interfaces_numpy
from compas_cra.viewers import cra_view, cra_view_ex
from compas_viewer import Viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.datastructures import Graph, Mesh
from compas.colors import Color
from compas.geometry import centroid_points, Point, Vector, Box, bounding_box
import numpy as np
from math import sqrt
from collections import defaultdict
from compas.files import OBJ

def is_feasible(assembly, solver: str, timer=False, verbose=False, density=1.0, d_bnd=0.001, eps=0.0001, mu=0.84):
    if solver == "RBE":
        testsolver = rbe_solve
    elif solver == "CRA":
        testsolver = cra_solve
    elif solver == "CRA_penalty":
        testsolver = cra_penalty_solve
    else:
        raise ValueError(f"Unknown solver, available options are 'RBE' or 'CRA'")
    try:
        testsolver(assembly, timer=timer, verbose=verbose, density=density, d_bnd=d_bnd, eps=eps, mu=mu)
        return True
    except Exception:
        return False
    
def is_feasible_penalty(assembly, timer=False, verbose=False, density=1.0, d_bnd=0.001, eps=0.0001, mu=0.84):
    try:
        cra_penalty_solve(assembly, timer=timer, verbose=verbose, density=density, d_bnd=d_bnd, eps=eps, mu=mu)
        return 
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

def idx_presort_z_recon(assembly, to_remove):

    idx_and_frames = []
    for idx in to_remove:
        block = assembly.node_block(idx)
        top_face = block.top()
        frame = block.face_frame(top_face)
        frame.flip()
        idx_and_frames.append((idx, frame))

    idx_and_frames.sort(key=lambda pair: pair[1].point.z, reverse=False)

    sorted_indices = [idx for idx, _ in idx_and_frames]
    return sorted_indices

def disassembly_workflow(assembly, goal_block, prints=True):

    remove = z_blockers(assembly, goal_block)

    remove_sorted = idx_presort_z(assembly, remove)
    remove_sorted.append(goal_block)

    mu = 0.9
    dispbnd = 1e-3 #1e-1
    overlap = 1e-3 #1e-3
    d = 1e-4

    final_disassembly_sequence = []
    disassembly_printout = []

    idx = 0
    ridx = 1 

    while idx < len(remove_sorted):
        i = remove_sorted[idx]
        if i in final_disassembly_sequence:
            idx += 1
            continue

        assembly.delete_block(i)

        if prints:
            print(f"Evaluating removal of block #{ridx} with index {i}")

        if is_feasible(assembly, solver="CRA", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
            if prints:
                print(f"Removal of block #{ridx} with index {i} is structurally feasible")
            final_disassembly_sequence.append(i)
            disassembly_printout.append(f"Removal of block #{ridx} with index {i} is structurally feasible")
            ridx += 1
            idx += 1

        else:
            if prints:
                print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible !!! trying cra_penalty_solve")

            fb = identify_failing_block(assembly)[0]

            if prints:
                print(f"Block with index {i} is unstable after removal of block #{ridx} with index {i}")

            if is_feasible(assembly, solver="CRA_penalty", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
                #get_forcesdirect(assembly)
                if prints:
                    print(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")
                
                final_disassembly_sequence.append(i)
                disassembly_printout.append(f"Removal of block #{ridx} with index {i} is structurally feasible with additional forces x...")
            
            ridx += 1

            if fb not in final_disassembly_sequence:
                if fb in remove_sorted:
                    fb_index = remove_sorted.index(fb)
                    if fb_index > idx:
                        # Remove from later and insert just after current
                        remove_sorted.pop(fb_index)
                        remove_sorted.insert(idx + 1, fb)
                else:
                    remove_sorted.insert(idx + 1, fb)

            else:
                print(f"!!! Removal of block #{ridx} with index {i} is structurally infeasible even with two-agent approach")
            
            idx += 1

    if print:
        print(f"Final disassembly sequence: {final_disassembly_sequence}")
        print(disassembly_printout)

    return final_disassembly_sequence


def resassembly_workflow(assembly, reassembly_file_path, prints=True):

    old_nodes = []
    for block in assembly.blocks():
        old_nodes.append(assembly.block_node(block))

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

    sorted_boxmeshes = sorted(boxmeshes, key=lambda m: m.centroid()[2])  # Z is index 2

    mu = 0.9
    dispbnd = 1e-3 #1e-1
    overlap = 1e-3 #1e-3
    d = 1e-4

    final_reassembly_sequence = []
    reassembly_printout = []


    for idx, m in enumerate(sorted_boxmeshes, start=1):

        assembly.add_block_from_mesh(m)
        assembly_interfaces_numpy(assembly, nmax=20, amin=1e-4, tmax=5.1)

        new_nodes = []
        for block in assembly.blocks():
            if assembly.block_node(block) not in old_nodes:
                new_nodes.append(assembly.block_node(block))
        bn = new_nodes[-1]     

        if prints:
            print("test")

        if is_feasible(assembly, solver="CRA", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
            if prints:
                print("test")
            final_reassembly_sequence.append(bn)
            reassembly_printout.append("test")

        else:
            if prints:
                print("test")
            if is_feasible(assembly, solver="CRA_penalty", verbose=False, timer=True, density=d, d_bnd=dispbnd, eps=overlap, mu=mu):
                if prints:
                    print("test")
                
                final_reassembly_sequence.append(bn)
                reassembly_printout.append("test")

    if print:
        print(f"Final reassembly sequence: {final_reassembly_sequence}")
        print(reassembly_printout)

    return final_reassembly_sequence

def identify_failing_block(assembly, support_node=0):

    block_force_map = defaultdict(float)

    for edge in assembly.graph.edges():
        u, v = edge
        # skip support node
        if support_node in (u, v):
            continue

        interfaces = assembly.graph.edge_attribute(edge, "interfaces")
        if not interfaces:
            continue
        for interface in interfaces:
            forces = interface.forces
            if not forces:
                continue
            #print(interface)

            frame = interface.frame
            w = frame.zaxis  # normal direction

            for force_data in forces:
                f_normal = force_data["c_np"] - force_data["c_nn"]
                #print(f_normal)
                magnitude = abs(f_normal)
                # Add to both blocks
                block_force_map[u] += magnitude / 2
                block_force_map[v] += magnitude / 2

    if not block_force_map:
        return None, 0.0  # fallback if all edges connect to support

    # Find block with max force contribution
    failing_block = max(block_force_map.items(), key=lambda item: item[0])
    return failing_block  # (block_id, force_magnitude)


def print_penalty_forces(assembly, scale=1.0):
    thres = 1e-6
    for edge in assembly.graph.edges():
        interfaces = assembly.graph.edge_attribute(edge, "interfaces")
        if interfaces is None:
            continue

        flip = assembly.graph.node_attribute(edge[0], "is_support") and not assembly.graph.node_attribute(edge[1], "is_support")

        for interface in interfaces:
            forces = interface.forces
            if not forces:
                continue

            corners = np.array(interface.points)
            frame = interface.frame
            w, u, v = frame.zaxis, frame.xaxis, frame.yaxis

            # Check if this interface is held by penalty tension
            #is_penalty = any(f["c_np"] - f["c_nn"] < -thres for f in forces)
            #if not is_penalty:
            #    continue

            is_pos = any(f["c_np"] - f["c_nn"] < -1 for f in forces)
            if not is_pos:
                continue

            # Compute net force vector
            sum_n = sum(f["c_np"] - f["c_nn"] for f in forces)
            sum_u = sum(f["c_u"] for f in forces)
            sum_v = sum(f["c_v"] for f in forces)
            resultant_f = (w * sum_n + u * sum_u + v * sum_v) * scale

            # Weighted position for visual clarity
            weights = [abs(f["c_np"] - f["c_nn"]) for f in forces]
            resultant_pos = np.average(corners, axis=0, weights=weights)

            if resultant_f.length < thres:
                continue

            print(resultant_pos, -resultant_f if flip else resultant_f)


""" def draw_penalty_forces(assembly, viewer, scale=1.0):
    thres = 1e-6
    for edge in assembly.graph.edges():
        interfaces = assembly.graph.edge_attribute(edge, "interfaces")
        if interfaces is None:
            continue

        # Determine if we need to flip arrow direction
        flip = assembly.graph.node_attribute(edge[0], "is_support") and not assembly.graph.node_attribute(edge[1], "is_support")

        for interface in interfaces:
            forces = interface.forces
            if not forces:
                continue

            corners = np.array(interface.points)
            frame = interface.frame
            w, u, v = frame.zaxis, frame.xaxis, frame.yaxis

            # Check if this interface is held by penalty tension
            is_penalty = any(f["c_np"] - f["c_nn"] < -thres for f in forces)
            if not is_penalty:
                continue

            # Compute net force vector
            sum_n = sum(f["c_np"] - f["c_nn"] for f in forces)
            sum_u = sum(f["c_u"] for f in forces)
            sum_v = sum(f["c_v"] for f in forces)
            resultant_f = (w * sum_n + u * sum_u + v * sum_v) * scale

            # Weighted position for visual clarity
            weights = [abs(f["c_np"] - f["c_nn"]) for f in forces]
            resultant_pos = np.average(corners, axis=0, weights=weights)

            if resultant_f.length < thres:
                continue

            arrow = Arrow(resultant_pos, -resultant_f if flip else resultant_f, linewidth=10)
            arrow.add_to_scene(viewer, facecolor=Color(1, 0, 0))  # Red = penalty
 """