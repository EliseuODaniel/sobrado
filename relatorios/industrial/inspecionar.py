import bpy,json
from pathlib import Path
from mathutils import Vector
rows=[]
for o in bpy.data.objects:
 if any(n in o.name for n in ["Rack", "Painel TV", "Armario", "Tabua mesa", "Banqueta", "Caixilho", "Pendente", "Louceiro", "Bancada", "porta", "Porta", "Junta piso"]):
  if o.type in {"MESH","EMPTY"}:
   corners=[o.matrix_world@Vector(v) for v in o.bound_box] if o.type=="MESH" else []
   rows.append({"name":o.name,"type":o.type,"location":list(o.matrix_world.translation),"bounds":[[min(p[i] for p in corners) for i in range(3)],[max(p[i] for p in corners) for i in range(3)]] if corners else [],"materials":[s.material.name if s.material else None for s in o.material_slots]})
Path("relatorios/industrial-v06/objetos-base.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2))
print("OBJECTS",len(rows))
print("CYCLES_TEXTURE_PROPERTIES",[p.identifier for p in bpy.context.scene.cycles.bl_rna.properties if "texture" in p.identifier or "cache" in p.identifier])
print("GLTF_AVAILABLE",hasattr(bpy.ops.export_scene,"gltf"))
print("BSDF_INPUTS",list(bpy.data.materials["IND07 Aco"].node_tree.nodes.get("Principled BSDF").inputs.keys()))
