import bpy,json
from pathlib import Path
p=Path('relatorios/atual-fiel-v02/fontes/scuba_suede_2k.blend')
with bpy.data.libraries.load(str(p.resolve()),link=False) as (src,dst):dst.materials=list(src.materials)
rows=[]
for m in dst.materials:
 if not m.use_nodes:continue
 for n in m.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':
   for x in n.inputs:
    if any(k in x.name for k in ['Specular','IOR','Anisotrop','Roughness']):rows.append({'socket':x.name,'from':[(l.from_node.name,l.from_socket.name) for l in x.links]})
 for n in m.node_tree.nodes:
  if n.type=='TEX_IMAGE':rows.append({'image_node':n.name,'image':n.image.filepath if n.image else None,'to':[(l.to_node.name,l.to_socket.name) for l in n.outputs['Color'].links]})
Path('relatorios/atual-fiel-v02/fontes/scuba-nodes.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2));print(json.dumps(rows,ensure_ascii=False))
