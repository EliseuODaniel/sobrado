import bpy,json
for o in bpy.data.objects:
 if o.type=="MESH" and ("pillow" in o.name.lower() or "almofada" in o.name.lower()):
  print(json.dumps({"name":o.name,"mesh":o.data.name,"vertices":len(o.data.vertices),"faces":len(o.data.polygons),"smooth":sum(p.use_smooth for p in o.data.polygons),"modifiers":[(m.name,m.type,getattr(m,"levels",None),getattr(m,"render_levels",None),m.show_render) for m in o.modifiers],"uv":list(o.data.uv_layers.keys()),"materials":[s.material.name if s.material else None for s in o.material_slots]},ensure_ascii=False))
