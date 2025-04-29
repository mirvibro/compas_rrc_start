# list of noteworthy findings/infos/peculiarities regarding our workflow

## mesh files rhino -> json compas:
rhino meshes when saved as json with rhinomeshobject_to_compas and compas.json_dump for some reason store vertices individually per mesh face, even if valence is >1; it's also not a closed mesh. I still have to figure out how this conversion happens internally and check how this affects our photogrammetry workflow. A normal mesh cube with 6 quad faces/8 vertices, after the saving it as json then has 24 vertices. Right now, it works after I use compas's Mesh.weld (even though it's a closed mesh in rhino), though there are still 24 vertices. 


## compas frames vs planes:

**in compas:**

frame = point + 2 vectors (x,y) =~ rhino plane      https://compas.dev/compas/latest/api/generated/compas.geometry.Frame.html

plane = point + normal vector      https://compas.dev/compas/latest/api/generated/compas.geometry.Plane.html

https://compas.dev/compas/2.6.1/userguide/basics.geometry.planes_and_frames.html
