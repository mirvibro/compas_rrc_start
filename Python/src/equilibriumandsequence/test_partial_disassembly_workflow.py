from sequence import scan_to_CRA_assembly, target_frames_by_z
from compas_cra.equilibrium import cra_penalty_solve, cra_solve, rbe_solve
from compas_cra.algorithms import assembly_interfaces_numpy
from compas_cra.viewers import cra_view, cra_view_ex
from compas_viewer import Viewer
from compas_viewer.scene import Tag, FrameObject, TagObject
from compas.datastructures import Graph
from compas.colors import Color
from compas.geometry import centroid_points

mesh_file_path = "C:\\Users\\michi\\Documents\\WORK\\TUrobo\\scripts\\filesrhinotocompas\\wall3.json"

assembly = scan_to_CRA_assembly(mesh_file_path)

assembly_interfaces_numpy(assembly, nmax=15, tmax=1e-6)



#print(graph.neighbors(goal_block))


def is_feasible(assembly, solver: str):
    if solver == "RBE":
        testsolver = rbe_solve
    elif solver == "CRA":
        solver == cra_solve
    else:
        raise ValueError(f"Unknown solver, available options are 'RBE' or 'CRA'")

    try:
        testsolver(assembly)
        return True
    except Exception:
        return False


""" if is_feasible(assembly, solver = "RBE"):
    print("Current assembly is feasible.")
    cra_view(assembly)
else:
    print("Current assembly is infeasible.") """



graph = assembly.graph
goal_block = 2
goal_block_z = assembly.node_point(goal_block).z
neighbors = []
neighbor_z = []
neighbors_above = []
neighbors_below = []


""" for neighbor in graph.neighbors(goal_block):
    point = assembly.node_point(neighbor)
    if point.z > goal_block_z:
        neighbors_above.append(neighbor)
    else:
        neighbors_below.append(neighbor)


if not neighbors_above:
    assembly.delete_block(goal_block)
    if is_feasible(assembly, solver="RBE"):
        print("Current assembly is feasible.")
        cra_view(assembly)
    else:
        print("Block is free but assembly seems to be unstable") """
        

def direct_z_blockers(testblock):
    z_test = assembly.node_point(testblock).z
    return [
        nbr for nbr in graph.neighbors(testblock)
        if assembly.node_point(nbr).z > z_test
    ]

def all_z_blockers(testblock, checked=None):
    if checked is None:
        checked = set()
    for nbr in direct_z_blockers(testblock):
        if nbr not in checked:
            checked.add(nbr)
            all_z_blockers(nbr, checked)
    return checked



#print(all_z_blockers(goal_block))




nodepoints = [] 
for block in assembly.blocks():
    node = assembly.block_node(block)
    nodepoints.append(assembly.node_point(node))
    #node_tags.append(Tag(block_node(block)))

# edges as structured internally
og_edges = []
for edge in assembly.edges():
    e = assembly.edge_line(edge)
    og_edges.append(e)



disassembly = assembly.copy()
blockers = all_z_blockers(goal_block)
for i in assembly.nodes():
    if i not in blockers and i != goal_block:
        disassembly.delete_block(i)


#target_frames = target_frames_by_z(disassembly, vis=True, tags=True)
""" 
viewer = Viewer()
#viewer.scene.add()
for order_nr, frame in enumerate(target_frames, start=1):
    tag = Tag(text=str(order_nr), position=frame.point)
    viewer.scene.add(tag)
for i in assembly.nodes():
    if i not in blockers and i != goal_block:
        viewer.scene.add(assembly.node_block(i), show_faces=True)
    elif i == goal_block:
        #vertexcolor = {vertex: Color.from_i(random()) for vertex in assembly.node_block(i).vertices()}
        viewer.scene.add(assembly.node_block(i), show_faces=True, color=Color(0, 0.1, 0.9))
    elif i in blockers:
        viewer.scene.add(assembly.node_block(i), show_faces=False)
viewer.renderer.camera.target = centroid_points(nodepoints)  
viewer.show()
 """

#cra_penalty_solve(assembly, verbose=True, timer=True)
#cra_solve(assembly)
#rbe_solve(assembly)

#cra_view(assembly)

""" viewer = Viewer()
viewer.scene.add(revised_edges)
for order_nr, node in enumerate(nodepoints):
        tag = Tag(text=str(order_nr), position=node)
        viewer.scene.add(tag)        
for block in assembly.blocks():
    viewer.scene.add(block, show_faces=False)
viewer.renderer.camera.target = centroid_points(nodepoints) """

""" cra_view_ex(assembly, viewer)     
viewer.show() """

