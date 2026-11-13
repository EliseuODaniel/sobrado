import bpy,json
print("LIBRARIES",[(l.name,l.filepath,l.users) for l in bpy.data.libraries])
print("LINKED_IDS",[(kind,d.name,d.library.filepath) for kind in ["objects","meshes","materials","images","node_groups","collections","curves"] for d in getattr(bpy.data,kind) if d.library][:30])
